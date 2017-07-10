"""
Django models for course certificates and related code
"""
import os
import uuid

from django.conf import settings
from django.db import models
from upload_validator import FileTypeValidator


def template_assets_path(instance, filename):
    """
    Returns the certificate template asset file path.

    Arguments:
            instance (CertificateTemplateAsset): An instance of CertificateTemplateAsset class
            filename (string): Name of the template asset file
    """
    from .controller import get_template_asset_path
    return get_template_asset_path(str(instance.id), filename)


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


class CertificateTemplate(models.Model):
    """
    Model for custom certificate django templates
    """
    name = models.CharField(max_length=255)
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    template = models.TextField()
    course_id = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CertificateTemplateAsset(models.Model):
    """
    Model for assets to be used in certificate templates i-e image, css files.
    """
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    asset = models.FileField(
        max_length=255,
        upload_to=template_assets_path,
        validators = [
            FileTypeValidator(
                allowed_types=[
                    'image/jpeg',
                    'image/png',
                    'image/gif',
                    'text/css',
                    'text/plain',
                    'application/javascript'
                ]
            )
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        save the certificate template asset
        """
        if self.pk is None:
            asset_file = self.asset
            self.asset = None
            super(CertificateTemplateAsset, self).save(*args, **kwargs)
            self.asset = asset_file

        super(CertificateTemplateAsset, self).save(*args, **kwargs)
