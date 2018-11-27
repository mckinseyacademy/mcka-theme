"""
Django models for course certificates and related code
"""
import uuid  # pylint: disable=unused-import

from django.db import models
from django.utils.translation import ugettext_lazy as _
from upload_validator import FileTypeValidator


def template_assets_path(instance, filename):
    """
    Returns the certificate template asset file path.

    Arguments:
            instance (CertificateTemplateAsset): An instance of
                                                 CertificateTemplateAsset class
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
    status = models.CharField(
        max_length=32,
        default=CertificateStatus.available
    )

    def as_json(self):
        return dict(
            id=self.id,
            course_id=self.course_id,
            status=self.status,
        )


class UserCourseCertificate(models.Model):
    """
    Model for generated certificates
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # pylint: disable=invalid-name
    user_id = models.IntegerField(unique=False)
    course_id = models.CharField(max_length=200, unique=False)
    email_sent = models.BooleanField(default=False)

    @property
    def uuid(self):
        """
        User course certificate model property to get unhyphenated uuid
        """
        return self.id.hex  # pylint: disable=no-member

    class Meta(object):
        """
        Meta class to set model meta options
        """
        unique_together = ('user_id', 'course_id',)


class CertificateTemplate(models.Model):
    """
    Model for custom certificate django templates
    """
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Description")
    )
    template = models.TextField(verbose_name=_("Template"))
    course_id = models.CharField(max_length=200, unique=True, verbose_name=_("Course ID"))
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
        verbose_name=_("Description"),
    )
    asset = models.FileField(
        max_length=255,
        upload_to=template_assets_path,
        verbose_name=_("Asset"),
        validators=[
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

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        """
        save the certificate template asset
        """
        if self.pk is None:
            asset_file = self.asset
            self.asset = None
            super(CertificateTemplateAsset, self).save(*args, **kwargs)
            self.asset = asset_file

        super(CertificateTemplateAsset, self).save(*args, **kwargs)
