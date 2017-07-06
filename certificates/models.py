"""
Django models for course certificates and related code
"""
import uuid

from django.db import models

class CertificateStatus(object):
    """
    Enum for certificate statuses
    """
    notavailable = 'notavailable'
    available = 'available'
    generating = 'generating'
    generated = 'generated'


class CourseCertificateStatus(models.Model):
    """
    Model for course certificates generation status
    """
    course_id = models.CharField(max_length=200, unique=True)
    status = models.CharField(max_length=32, default=CertificateStatus.available)

    def as_json(self):
        return dict(
            id = self.id,
            course_id = self.course_id,
            status = self.status,
        )


class UserCourseCertificate(models.Model):
    """
    Model for generated certificates
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.IntegerField(unique=False)
    course_id = models.CharField(max_length=200, unique=False)
    email_sent = models.BooleanField(default=False)

    @property
    def uuid(self):
        """
        User course certificate model property to get unhyphenated uuid
        """
        return self.id.hex


    class Meta:
        """
        Meta class to set model meta options
        """
        unique_together = ('user_id', 'course_id',)
