from django.contrib.auth.models import AbstractBaseUser
from django.db import models

class RemoteUser(AbstractBaseUser):
    id = models.UUIDField(primary_key=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)

    USERNAME_FIELD = "email"

    def has_perm(self, perm, obj=None):
        return True      # because FastAPI does permissions

    def has_module_perms(self, app_label):
        return True
