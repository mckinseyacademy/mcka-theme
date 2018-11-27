import binascii

from os import urandom
from django.db import models as db_models


class ApiToken(db_models.Model):
    client_id = db_models.IntegerField(default=0, unique=True)
    token = db_models.CharField(max_length=200, unique=True, db_index=True)
    created_at = db_models.DateTimeField(auto_now_add=True)
    updated_at = db_models.DateTimeField(auto_now=True)

    def as_json(self):
        return dict(
            id=self.id,
            client_id=self.client_id,
            token=self.token,
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat(),
        )

    def save(self):
        if not self.id:
            self.token = binascii.hexlify(urandom(32))
        super(ApiToken, self).save()
