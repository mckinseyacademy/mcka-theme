"""
Tests for certificates django models
"""
from lib.utils import DottableDict

from django.test import TestCase
from django.db import IntegrityError

from courses.models import FeatureFlags

from ..models import UserCourseCertificate, CertificateTemplate


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

    def test_course_certificate_feature(self):
        """
        Test if certificates are disabled by default for course
        """
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

    def test_certificate_uniqueness(self):
        """
        Test user course certificate uniqueness on course_id and user_id
        """
        UserCourseCertificate.objects.create(
            course_id=self.course_id,
            user_id=self.user.id
        )

        with self.assertRaises(IntegrityError):
            UserCourseCertificate.objects.create(
                course_id=self.course_id,
                user_id=self.user.id
            )


class CertificateTemplateModelTest(TestCase):
    """
    Test the Certificate Template Model.
    """
    def setUp(self):
        """
        Setup Certificate Template model test
        """
        super(CertificateTemplateModelTest, self).setUp()
        self.course_id = 'test/course/302'
        self.template = '<p>dummy</p>'

    def test_template_course_uniqueness(self):
        """
        Test  certificate template uniqueness on course
        """
        CertificateTemplate.objects.create(
            course_id=self.course_id,
            template=self.template
        )

        with self.assertRaises(IntegrityError):
            CertificateTemplate.objects.create(
                course_id=self.course_id,
                template=self.template
            )
