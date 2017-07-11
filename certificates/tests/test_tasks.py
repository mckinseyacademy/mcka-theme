"""
Tests for certificates tasks
"""
from lib.util import DottableDict

from django.core import mail
from django.test import TestCase, override_settings

from accounts.tests import ApplyPatchMixin

from ..models import (
    CertificateStatus,
    UserCourseCertificate,
    CourseCertificateStatus
)
from ..tasks import generate_course_certificates_task


def mock_passed_users_list():
    """
    Helper method to mock passed users list
    """
    return [
        DottableDict({
            "id": 2,
            "email": "ecommerce_worker@fake.email",
            "username": "ecommerce_worker"
        }),
        DottableDict({
            "id": 5,
            "email": "honor@example.com",
            "username": "honor"
        }),
        DottableDict({
            "id": 6,
            "email": "audit@example.com",
            "username": "audit"
        }),
        DottableDict({
            "id": 8,
            "email": "verified@example.com",
            "username": "verified"
        })
    ]


class CertificateTaskTest(TestCase, ApplyPatchMixin):
    """
    Test the Course Certificates background tasks.
    """
    def setUp(self):
        """
        Setup certificate task test
        """
        super(CertificateTaskTest, self).setUp()
        self.course_id = 'test/course/302'
        self.passed_user_ids = [2, 5, 6, 8]
        self.passed_users = mock_passed_users_list()

    def _apply_course_and_user_api_patch(self):
        """
        Helper method to patch user and course api
        """
        course_api = self.apply_patch('certificates.controller.course_api')
        course_api.get_course_passed_users_id_list.return_value = self.passed_user_ids
        user_api = self.apply_patch('certificates.controller.user_api')
        user_api.get_users.return_value = self.passed_users

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_generate_course_certificates_task(self):
        """
        Test generate course certificates task
        """
        self._apply_course_and_user_api_patch()
        CourseCertificateStatus.objects.create(
            course_id=self.course_id,
            status=CertificateStatus.generating
        )

        # generate course certificates
        base_domain = 'https://test.com'
        generate_course_certificates_task.delay(self.course_id, base_domain)

        # test if emails sent to all passed users
        self.assertEqual(len(mail.outbox), len(self.passed_users))
        sent_emails_addresses = [email.to[0] for email in mail.outbox]
        for user in self.passed_users:
            self.assertIn(user.email, sent_emails_addresses)

        # test if certificate entries added to database
        generated_certificates = UserCourseCertificate.objects.filter(
            course_id=self.course_id
        )
        self.assertEqual(len(generated_certificates), len(self.passed_users))
        for user in self.passed_users:
            self.assertEqual(
                UserCourseCertificate.objects.filter(
                    course_id=self.course_id, user_id=user.id
                ).count(),
                1
            )

        course_certificate_status = CourseCertificateStatus.objects.get(
            course_id=self.course_id
        )
        self.assertEqual(
            course_certificate_status.status,
            CertificateStatus.generated
        )
