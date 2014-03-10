from django.db import models
from django.contrib.auth.models import AbstractBaseUser

# Create your models here.
class RemoteUser(AbstractBaseUser):
    session_key = models.CharField('session_key', max_length = 2000, unique = True)

    def __init__(session_key):
        self.session_key = session_key

    USERNAME_FIELD = "session_key"