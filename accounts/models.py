from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import CompanyUnit

class User(AbstractUser):
    company_unit = models.ForeignKey(CompanyUnit, null=True, blank=True, on_delete=models.SET_NULL)
    is_admin_local = models.BooleanField(default=False)
