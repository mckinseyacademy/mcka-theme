"""
Tests for certificates django views
"""
import uuid
import datetime
from functools import wraps
import ddt

from lib.utils import DottableDict
from mock import patch

from django.test import TestCase
from django.test.client import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.conf import settings  # noqa: F401
from django.utils.decorators import available_attrs
from courses.models import FeatureFlags
from accounts.tests.utils import ApplyPatchMixin
from courses.tests.test_controllers import MockCourseAPI

from ..models import (  # noqa: F401
    UserCourseCertificate,
    CertificateStatus,
    CourseCertificateStatus,
    CertificateTemplateAsset,
    CertificateTemplate
)
from ..forms import CertificateTemplateAssetForm, CertificateTemplateForm  # noqa: F401

GENERATE_CERTIFICATES_TASK_DATA = [
    (True, datetime.datetime.now() + datetime.timedelta(days=4)),
    (False, datetime.datetime.now() - datetime.timedelta(days=4)),
    (False, datetime.datetime.now() + datetime.timedelta(days=4)),
    (True, datetime.datetime.now() - datetime.timedelta(days=4)),
]

_FAKE_USER_OBJ = DottableDict({
    "id": 2,
    "email": "ecommerce_worker@fake.email",
    "username": "ecommerce_worker",
    "full_name": "Ecommerce worker",
    "is_internal_admin": False,
    "is_authenticated": True,
})


def _get_course_certificate_status(course_id):
    """
    Returns user course certificate given course and user id
    """
    course_certificate_status = None
    try:
        course_certificate_status = CourseCertificateStatus.objects.get(
            course_id=course_id
        )
    except CourseCertificateStatus.DoesNotExist:
        pass

    return course_certificate_status


def _fake_permission_group_required(*group_names):  # pylint: disable=unused-argument
    """
    Fake method for permission_group_required method
    """

    def decorator(view_fn):
        def _wrapped_view(request, *args, **kwargs):
            # faking request user
            request.user = _FAKE_USER_OBJ
            return view_fn(request, *args, **kwargs)

        return wraps(view_fn, assigned=available_attrs(view_fn))(_wrapped_view)

    return decorator


permission_patcher = patch(  # pylint: disable=invalid-name
    'lib.authorization.permission_group_required',
    _fake_permission_group_required
).start()


@ddt.ddt
class CertificateViewTest(TestCase, ApplyPatchMixin):
    """
    Test the Course Certificate Views.
    """

    def setUp(self):
        """
        Setup course certificate model test
        """
        super(CertificateViewTest, self).setUp()
        self.client = Client()

        # TODO: 504 issue fix - uncomment this when original commit is included in release
        # self.client.login(user_role=PERMISSION_GROUPS.MCKA_ADMIN)
        # self.user = auth.get_user(self.client)
        #
        # self.mock_user_api_data_manager(
        #     module_paths=[
        #         'accounts.middleware.thread_local.UserDataManager',
        #     ],
        #     data={'courses': [], 'current_course': None}
        # )

        self.courses = [
            ('abc/123/test', 'Abc Course'),
            ('xyz/334/dummy', 'Xyz Course'),
            ('ggg/667/dummy', 'GGG Course')
        ]
        self.course = MockCourseAPI.get_course(self.courses[0][0])
        self.user = DottableDict({
            "id": 2,
            "email": "ecommerce_worker@fake.email",
            "username": "ecommerce_worker",
            "full_name": "Ecommerce worker"
        })
        self.user_course_certificate = UserCourseCertificate.objects.create(
            course_id=self.courses[0][0],
            user_id=self.user.id
        )
        self.template_asset_post_data = {'description': 'dumy description'}
        self.stylesheet = SimpleUploadedFile(
            'styles.css',
            'dummy content',
            content_type='text/css'
        )
        self.template_asset_file_data = {'asset': self.stylesheet}
        self.template_assets = [
            CertificateTemplateAssetForm(
                self.template_asset_post_data,
                self.template_asset_file_data
            ).save()
        ]

        self.templates = []
        self.template_post_data = {
            'name': 'test',
            'description': 'dummy',
            'template': '<p>dummy template</p>',
            'course_id': self.courses[2][0]
        }
        for x in xrange(2):
            self.templates.append(
                CertificateTemplate.objects.create(
                    name='test',
                    description='dummy',
                    template='<p>dummy template</p>',
                    course_id=self.courses[x][0]
                )

            )

    def _apply_patch(self):
        """
        Helper method to patch user and course api
        """
        user_api = self.apply_patch('certificates.views.user_api')
        user_api.get_user.return_value = self.user
        course_api = self.apply_patch('certificates.views.course_api')
        course_api.get_user.return_value = self.course

    def _apply_get_courses_choice_list_patch(self):
        """
        Helper method to patch get_courses_choice_list_patch method
        """

        get_courses_choice_list = self.apply_patch(
            'certificates.forms.get_courses_choice_list'
        )
        get_courses_choice_list.return_value = self.courses

    def test_get_certificate_by_uuid_invalid_uuid(self):
        """
        Test get certificate by uuid view with invalid uuid
        """
        self._apply_patch()
        invalid_certificate_url = reverse(
            'get_certificate_by_uuid',
            kwargs={'certificate_uuid': uuid.uuid4().hex}
        )
        response = self.client.get(invalid_certificate_url)
        self.assertEqual(response.status_code, 404)

    def test_get_certificate_by_uuid_valid_uuid(self):
        """
        Test get certificate by uuid view with valid uuid
        """
        self._apply_patch()
        valid_certificate_url = reverse(
            'get_certificate_by_uuid',
            kwargs={'certificate_uuid': self.user_course_certificate.uuid}
        )
        response = self.client.get(valid_certificate_url)
        self.assertEqual(response.status_code, 200)

    @ddt.data(*GENERATE_CERTIFICATES_TASK_DATA)
    @ddt.unpack
    def test_generate_course_certificates(
            self, certs_feature_flag, course_end_date
    ):
        """
        Test generate course certificates view
        """
        generate_certificate_url = reverse(
            'generate_course_certificates',
            args=(self.courses[0][0],)
        )
        FeatureFlags.objects.create(
            course_id=self.courses[0][0],
            certificates=certs_feature_flag
        )
        data = {'course_end': course_end_date}
        expected_url = reverse(
            'course_details',
            kwargs={'course_id': self.courses[0][0]}
        )

        response = self.client.post(generate_certificate_url, data)

        self.assertRedirects(
            response,
            expected_url=expected_url,
            status_code=302,
            target_status_code=302
        )
        course_certificate_status = _get_course_certificate_status(
            self.courses[0][0]
        )

        if certs_feature_flag and course_end_date < datetime.datetime.now():
            self.assertIsNotNone(course_certificate_status)
            self.assertEqual(
                course_certificate_status.status,
                CertificateStatus.generating
            )
        else:
            self.assertIsNone(course_certificate_status)

    # TODO: mock API to fix test and uncomment
    # def test_certificate_template_assets_get(self):
    #     """
    #     Test get certificate template assets view
    #     """
    #     response = self.client.get(reverse('certificate_template_assets'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsInstance(
    #         response.context['form'],
    #         CertificateTemplateAssetForm
    #     )
    #     self.assertEqual(
    #         len(response.context['certificate_template_assets']),
    #         len(self.template_assets)
    #    )

    # TODO: mock API to fix test and uncomment
    # def test_template_assets_post_invalid(self):
    #     """
    #     Test post certificate template assets view with invalid data
    #     """
    #     response = self.client.post(
    #         reverse('certificate_template_assets'),
    #         self.template_asset_post_data
    #     )
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsInstance(
    #         response.context['form'],
    #         CertificateTemplateAssetForm
    #     )
    #     self.assertEqual(
    #         len(response.context['certificate_template_assets']),
    #         len(self.template_assets)
    #     )
    #     self.assertTrue(response.context['form'].errors)

    # TODO: mock API to fix test and uncomment
    # def test_certificate_templates(self):
    #     """
    #     Test get certificate templates view
    #     """
    #     response = self.client.get(reverse('certificate_templates'))
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(
    #         len(response.context['certificate_templates']),
    #         len(self.templates)
    #     )

    # TODO: mock API to fix test and uncomment
    # def test_new_certificate_template_get(self):
    #     """
    #     Test get new certificate template view
    #     """
    #     response = self.client.get(reverse('new_certificate_template'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsInstance(response.context['form'], CertificateTemplateForm)

    # TODO: mock API to fix test and uncomment
    # def test_new_certificate_template_post_valid(self):
    #     """
    #     Test post new certificate template view with valid data
    #     """
    #     self._apply_get_courses_choice_list_patch()
    #     response = self.client.post(
    #         reverse('new_certificate_template'),
    #         self.template_post_data
    #     )
    #
    #     self.assertRedirects(
    #         response,
    #         expected_url=reverse('certificate_templates'),
    #         status_code=302,
    #         target_status_code=200
    #     )
    #     certificate_templates = CertificateTemplate.objects.all()
    #     self.assertEqual(len(certificate_templates), len(self.templates) + 1)

    # TODO: mock API to fix test and uncomment
    # def test_new_template_post_invalid(self):
    #     """
    #     Test post new certificate template view with invalid data
    #     """
    #     response = self.client.post(
    #         reverse('new_certificate_template'),
    #         self.template_post_data
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     certificate_templates = CertificateTemplate.objects.all()
    #     self.assertEqual(len(certificate_templates), len(self.templates))
    #     self.assertIsInstance(response.context['form'], CertificateTemplateForm)

    # TODO: mock API to fix test and uncomment
    # def test_edit_certificate_template_get(self):
    #     """
    #     Test get edit certificate template view
    #     """
    #     response = self.client.get(
    #         reverse(
    #             'edit_certificate_template',
    #             kwargs={'template_id': self.templates[0].id}
    #         )
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsInstance(response.context['form'], CertificateTemplateForm)
    #     self.assertEqual(
    #         response.context['form'].initial['course_id'],
    #         self.templates[0].course_id
    #     )

    # TODO: mock API to fix test and uncomment
    # def test_edit_certificate_template_post_valid(self):
    #     """
    #     Test post edit certificate template view with valid data
    #     """
    #     self._apply_get_courses_choice_list_patch()
    #     new_template_description = 'updated description'
    #     self.template_post_data['description'] = new_template_description
    #     response = self.client.post(
    #         reverse(
    #             'edit_certificate_template',
    #             kwargs={'template_id': self.templates[0].id}
    #         ),
    #         self.template_post_data
    #     )
    #
    #     self.assertRedirects(
    #         response,
    #         expected_url=reverse('certificate_templates'),
    #         status_code=302,
    #         target_status_code=200
    #     )
    #     certificate_template = CertificateTemplate.objects.get(
    #         id=self.templates[0].id
    #     )
    #     self.assertEqual(
    #         certificate_template.description, new_template_description
    #     )

    # TODO: mock API to fix test and uncomment
    # def test_edit_template_post_invalid(self):
    #     """
    #     Test post edit certificate template view with invalid data
    #     """
    #     response = self.client.post(
    #         reverse(
    #             'edit_certificate_template',
    #             kwargs={'template_id': self.templates[0].id}
    #         ),
    #         self.template_asset_post_data
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsInstance(response.context['form'], CertificateTemplateForm)

    def test_load_template_asset(self):
        """
        Test load template asset view
        """
        response = self.client.get(
            reverse(
                'load_template_asset',
                kwargs={
                    'asset_id': self.template_assets[0].id,
                    'asset_name': self.stylesheet.name
                }
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEquals(
            response.get('Content-Disposition'),
            'attachment; filename={}'.format(self.stylesheet.name)
        )

    def test_load_template_asset_invalid_path(self):
        """
        Test load template asset view with invalid path
        """
        response = self.client.get(
            reverse(
                'load_template_asset',
                kwargs={'asset_id': 999, 'asset_name': 'dummy.txt'}
            )
        )
        self.assertEqual(response.status_code, 404)
