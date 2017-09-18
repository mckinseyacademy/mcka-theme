"""
Tests for certificates controllers
"""
import os
import uuid
import datetime
import ddt
from lib.utils import DottableDict

from django.core import mail
from django.test import TestCase
from django.conf import settings

from courses.models import FeatureFlags
from accounts.tests.tests import ApplyPatchMixin
from .test_tasks import mock_passed_users_list
from .test_views import GENERATE_CERTIFICATES_TASK_DATA
from ..controller import (
    get_course_certificates_status,
    get_course_passed_users_list,
    generate_user_course_certificate,
    send_certificate_generation_email,
    get_certificate_template,
    get_courses_choice_list,
    get_template_asset_path,
)
from ..models import (
    CertificateStatus,
    UserCourseCertificate,
    CertificateTemplate
)


def _get_user_course_certificate(course_id, user_id):
    """
    Returns user course certificate given course and user id
    """
    try:
        certificate = UserCourseCertificate.objects.get(
            course_id=course_id,
            user_id=user_id
        )
    except UserCourseCertificate.DoesNotExist:
        certificate = None

    return certificate


@ddt.ddt
class CertificateControllerTest(TestCase, ApplyPatchMixin):
    """
    Test the Course Certificates.
    """
    def setUp(self):
        """
        Setup certificate controller test
        """
        super(CertificateControllerTest, self).setUp()
        self.course_id = 'test/course/302'
        self.passed_user_ids = [2, 5, 6, 8]
        self.passed_users = mock_passed_users_list()

        self.paginated_passed_users = DottableDict({
            "results": self.passed_users,
            "num_pages": 1
        })

        self.courses = [
            DottableDict({
                "id": "abc/123/test",
                "name": "abc 123 test",
                "category": "course"
            }),
            DottableDict({
                "id": "xyz/123/test",
                "name": "xyz 123 test",
                "category": "course"
            }),
        ]

        self.certificate_template = CertificateTemplate(
            name='test',
            description='dummy',
            template='<p>dummy template</p>',
            course_id=self.course_id
        )

    @ddt.data(*GENERATE_CERTIFICATES_TASK_DATA)
    @ddt.unpack
    def test_get_course_certificates_status(
            self, certs_feature_flag, course_end_date
        ):
        """
        Test course certificates status
        """
        # if feature flags not exist
        course_certificates_status = get_course_certificates_status(
            self.course_id,
            course_end_date
        )
        self.assertEqual(
            course_certificates_status,
            CertificateStatus.notavailable
        )

        FeatureFlags.objects.create(
            course_id=self.course_id,
            certificates=certs_feature_flag
        )

        course_certificates_status = get_course_certificates_status(
            self.course_id,
            course_end_date
        )
        if certs_feature_flag and course_end_date < datetime.datetime.now():
            self.assertEqual(
                course_certificates_status,
                CertificateStatus.available
            )
        else:
            self.assertEqual(
                course_certificates_status,
                CertificateStatus.notavailable
            )

    def test_send_certificate_generation_email(self):
        """
        Test send certificate generation email
        """
        self.assertEqual(len(mail.outbox), 0)
        base_domain = 'https://test.com'
        send_certificate_generation_email(
            self.course_id,
            self.passed_users[0],
            uuid.uuid4().hex,
            base_domain
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(self.passed_users[0].email, mail.outbox[0].to[0])

    def test_get_course_passed_users_list(self):
        """
        Test course passed users list get
        """
        course_api = self.apply_patch('certificates.controller.course_api')
        course_api.get_course_passed_users.return_value = self.paginated_passed_users

        returned_passed_users = get_course_passed_users_list(self.course_id)
        self.assertEqual(returned_passed_users, self.passed_users)

    def test_generate_course_certificate(self):
        """
        Test course user certificate generate
        """
        user = self.passed_users[0]

        certificate = _get_user_course_certificate(self.course_id, user.id)

        self.assertIsNone(certificate)

        generate_user_course_certificate(self.course_id, user)

        certificate = _get_user_course_certificate(self.course_id, user.id)

        self.assertIsNotNone(certificate)
        self.assertTrue(
            certificate.course_id == self.course_id and
            certificate.user_id == user.id
        )

    def test_get_certificate_template(self):
        """
        Test get certificate template helper method
        """
        template = get_certificate_template(self.course_id)
        self.assertIsNone(template)

        self.certificate_template.save()
        template = get_certificate_template(self.course_id)
        self.assertIsInstance(template, CertificateTemplate)

    def test_get_courses_choice_list(self):
        """
        Test get courses choice list helper method
        """
        course_api = self.apply_patch('certificates.controller.course_api')
        course_api.get_course_list.return_value = self.courses

        courses = get_courses_choice_list()
        self.assertEqual(
            courses,
            [(course.id, course.name) for course in self.courses]
        )

    def test_get_template_asset_path(self):
        """
        Test get template asset path helper method
        """
        asset_id = '5'
        asset_name = 'dummy.txt'
        expected_path = os.path.join(
            settings.BASE_CERTIFICATE_TEMPLATE_ASSET_PATH,
            asset_id,
            asset_name
        )

        asset_path = get_template_asset_path(asset_id, asset_name)
        self.assertEqual(asset_path, expected_path)
