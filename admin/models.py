from django.db import models
from api_client import group_api

# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=255)

    client_group_id = models.CharField(max_length=255)

    def save(self, **kwargs):
        if not self.client_group_id:
            self.client_group_id = group_api.create_group("{}_COMPANY".format(self.name)).id

        super(Client, self).save(**kwargs)

    def __unicode__(self):
        return self.name
