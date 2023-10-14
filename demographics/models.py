from django.db import models

from datetime import date


# Create your models here.
class Gender(models.Model):
    """Genders for all Users"""

    gender_name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.id} {self.gender_name}"


class ScholarshipType(models.Model):
    """Scholarship Types"""

    scholarship_name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.scholarship_name}"


"""
class Applicant(models.Model):
    # Applicant's Demographics

    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    middlename = models.CharField(max_length=30, null=True)
    gender = models.ForeignKey(
        Gender, on_delete=models.CASCADE, default=3
    )  # 1 - Male, 2 - Female, 3 - Undefined
    contactnumber = models.CharField(max_length=13)  # +639xxxxxxxxx
    house_address = models.CharField(max_length=50)
    barangay = models.CharField(max_length=30)
    district = models.PositiveSmallIntegerField(null=True)
    religion = models.CharField(max_length=30)

    facebookLink = models.CharField(
        max_length=100, unique=True
    )  # www.facebook.com/username

    email = models.EmailField(unique=True)
    yearsOfResidency = models.PositiveSmallIntegerField(null=False)
    birthdate = models.DateField()

    def calculate_age(self):
        today = date.today()
        age = (
            today.year
            - self.birthdate.year
            - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        )
        return age

    def save(self, *args, **kwargs):
        self.age = self.calculate_age()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} | {self.lastname}, {self.firstname} | {self.email}"
"""