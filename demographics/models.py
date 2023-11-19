from django.db import models

from datetime import date


# Create your models here.
class Gender(models.Model):
    """Genders for all Users"""

    gender_name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.gender_name}"