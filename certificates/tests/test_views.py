"""
Tests for certificates django views
"""
import uuid
import ddt
import datetime
from functools import wraps
from lib.util import DottableDict
from mock import patch

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils.decorators import available_attrs

from courses.tests import MockCourseAPI
from accounts.tests import ApplyPatchMixin
from courses.models import FeatureFlags

from ..models import UserCourseCertificate, CertificateStatus, CourseCertificateStatus


def _fake_permission_group_required(*group_names):
    """
    Fake method for permission_group_required method
    """
    def decorator(view_fn):
        def _wrapped_view(request, *args, **kwargs):
            return view_fn(request, *args, **kwargs)
        return wraps(view_fn, assigned=available_attrs(view_fn))(_wrapped_view)
    return decorator


permission_patcher = patch(
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
        self.course_id = 'test/course/302'
        self.course = MockCourseAPI.get_course(self.course_id)
        self.user = DottableDict({
            "id": 2,
            "email": "ecommerce_worker@fake.email",
            "username": "ecommerce_worker"
        })
        self.user_course_certificate = UserCourseCertificate.objects.create(
            course_id = self.course_id,
            user_id = self.user.id
        )

    def _apply_patch(self):
        """
        Helper method to patch user and course api
        """
        user_api = self.apply_patch('certificates.views.user_api')
        user_api.get_user.return_value = self.user
        course_api = self.apply_patch('certificates.views.course_api')
        course_api.get_user.return_value = self.course

    def _get_course_certificate_status(self, course_id):
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

    @ddt.data(
        (True, datetime.datetime.now() + datetime.timedelta(days=4)),
        (False, datetime.datetime.now() - datetime.timedelta(days=4)),
        (False, datetime.datetime.now() + datetime.timedelta(days=4)),
        (True, datetime.datetime.now() - datetime.timedelta(days=4)),
    )
    @ddt.unpack
    def test_generate_course_certificates(self, certs_feature_flag, course_end_date):
        """
        Test generate course certificates view
        """
        generate_certificate_url = reverse(
            'generate_course_certificates',
            args=(self.course_id, )
        )
        features = FeatureFlags.objects.create(course_id=self.course_id, certificates=certs_feature_flag)
        data = {'course_end': course_end_date}
        expected_url=reverse('course_details', kwargs={'course_id': self.course_id})


        response = self.client.post(generate_certificate_url, data)

        self.assertRedirects(
            response,
            expected_url=expected_url,
            status_code=302,
            target_status_code=302
        )
        course_certificate_status = self._get_course_certificate_status(self.course_id)

        if certs_feature_flag and course_end_date < datetime.datetime.now():
            self.assertIsNotNone(course_certificate_status)
            self.assertEqual(course_certificate_status.status, CertificateStatus.generating)
        else:
            self.assertIsNone(course_certificate_status)
