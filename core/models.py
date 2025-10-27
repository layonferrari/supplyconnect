from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    """Modelo base com data de criação e atualização automática."""
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CompanyUnit(TimeStampedModel):
    """Filial/Unidade da empresa."""
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)  # Ex.: BR, IT, ES...
    default_language = models.CharField(max_length=16, default="pt-br")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"
