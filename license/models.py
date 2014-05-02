from django.db import models

# Create your models here.
class LicenseGrant(models.Model):
    license_uuid = models.CharField(max_length=36)

    # with what is the license associated (e.g. course)
    granted_id = models.IntegerField()

    # the owner of the license (e.g. Organisation)
    grantor_id = models.IntegerField()

    # to whom was the licence granted (e.g. user enrolled in course)
    grantee_id = models.IntegerField(null=True,blank=True)

    # when was the grant allowed
    granted_on = models.DateTimeField(null=True,blank=True)

    def save(self):
        if self.license_uuid is None:
            self.license_uuid = str(uuid.uuid4())

        super(LicenseGrant, self).save()
