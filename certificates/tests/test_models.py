"""
Tests for certificates django models
"""
from lib.util import DottableDict

from django.test import TestCase
from django.db import IntegrityError

from courses.models import FeatureFlags
from courses.tests import MockCourseAPI

from ..models import UserCourseCertificate, CourseCertificateStatus


class CourseCertificateStatusModelTest(TestCase):
    """
    Test the Course Certificate Model.
    """
    def setUp(self):
        """
        Setup course certificate model test
        """
        super(CourseCertificateStatusModelTest, self).setUp()
        self.course_id = 'test/course/302'

    def test_course_certificate_disabled_by_default(self):
        """
        Test if certificates are disabled by default for course
        """
        course = MockCourseAPI.get_course(self.course_id)
        feature_flags = FeatureFlags.objects.create(course_id=self.course_id)
        self.assertFalse(feature_flags.certificates)


class UserCourseCertificateModelTest(TestCase):
    """
    Test the User Course Certificate Model.
    """
    def setUp(self):
        """
        Setup user course certificate model test
        """
        super(UserCourseCertificateModelTest, self).setUp()
        self.course_id = 'test/course/302'
        self.user = DottableDict({
            "id": 2,
            "email": "ecommerce_worker@fake.email",
            "username": "ecommerce_worker"
        })

    def test_user_course_certificate_uniqueness(self):
        """
        Test user course certificate uniqueness on course_id and user_id
        """
        certificate = UserCourseCertificate.objects.create(
            course_id=self.course_id,
            user_id=self.user.id
        )

        with self.assertRaises(IntegrityError):
            certificate = UserCourseCertificate.objects.create(
                course_id=self.course_id,
                user_id=self.user.id
            )
