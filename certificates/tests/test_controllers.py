"""
Tests for certificates controllers
"""
import uuid
import datetime
import ddt
from lib.util import DottableDict

from django.core import mail
from django.test import TestCase

from courses.models import FeatureFlags
from courses.tests import MockCourseAPI
from accounts.tests import ApplyPatchMixin
from ..controller import (
    get_course_certificates_status,
    get_course_passed_users,
    generate_user_course_certificate,
    send_certificate_generation_email
)
from ..models import CertificateStatus, UserCourseCertificate


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
        self.passed_user_ids = [2,5,6,8]
        self.passed_users = [
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

    def _get_user_course_certificate(self, course_id, user_id):
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

    @ddt.data(
        (True, datetime.datetime.now() + datetime.timedelta(days=4)),
        (False, datetime.datetime.now() - datetime.timedelta(days=4)),
        (False, datetime.datetime.now() + datetime.timedelta(days=4)),
        (True, datetime.datetime.now() - datetime.timedelta(days=4)),
    )
    @ddt.unpack
    def test_get_course_certificates_status(self, certs_feature_flag, course_end_date):
        """
        Test course certificates status
        """
        features = FeatureFlags.objects.create(course_id=self.course_id, certificates=certs_feature_flag)

        course_certificates_status = get_course_certificates_status(
            self.course_id,
            course_end_date
        )
        if certs_feature_flag and course_end_date < datetime.datetime.now():
            self.assertEqual(course_certificates_status, CertificateStatus.available)
        else:
            self.assertEqual(course_certificates_status, CertificateStatus.notavailable)

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

    def test_get_course_passed_users(self):
        """
        Test course passed users list get
        """
        course_api = self.apply_patch('certificates.controller.course_api')
        course_api.get_course_passed_users_id_list.return_value = self.passed_user_ids

        user_api = self.apply_patch('certificates.controller.user_api')
        user_api.get_users.return_value = self.passed_users

        returned_passed_users = get_course_passed_users(self.course_id)
        self.assertEqual(returned_passed_users, self.passed_users)

    def test_generate_course_certificate(self):
        """
        Test course user certificate generate
        """
        user = self.passed_users[0]

        certificate = self._get_user_course_certificate(self.course_id, user.id)

        self.assertIsNone(certificate)

        generate_user_course_certificate(self.course_id, user)

        certificate = self._get_user_course_certificate(self.course_id, user.id)

        self.assertIsNotNone(certificate)
        self.assertTrue(
            certificate.course_id == self.course_id and certificate.user_id == user.id
        )
