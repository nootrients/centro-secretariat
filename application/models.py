from django.db import models

from accounts.models import Officer

from datetime import date
import uuid

# Create your models here.
class AcademicYearField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 9
        kwargs['editable'] = False
        kwargs['default'] = self.calculate_academic_year()
        
        super().__init__(*args, **kwargs)

    def calculate_academic_year(self):
        today = date.today()
        current_year = today.year
        next_year = current_year + 1

        return f"{current_year}-{next_year}" 


class Applications(models.Model):
    class ScholarshipType(models.TextChoices):
        HONORS = "HONORS", "Honors"
        PREMIER = "PREMIER", "Premier"
        PRIORITY = "PRIORITY", "Priority"
        BASIC_PLUS = "BASIC PLUS", "Basic Plus"
        BASIC = "BASIC", "Basic"
        SUC_LCU = "SUC_LCU", "SUC/LCU"
        REVIEW = "REVIEW", "Review"
        LEAD = "LEAD", "Lead"

    class Semester(models.TextChoices):
        FIRST_SEMESTER = "FIRST SEMESTER", "First Semester"
        SECOND_SEMESTER = "SECOND SEMESTER", "Second Semester"

    application_uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    
    scholarship_type = models.CharField(
        max_length=20,
        null = False,
        choices=ScholarshipType.choices, 
        default=ScholarshipType.BASIC
    )

    academic_year = AcademicYearField()
    
    semester = models.CharField(
        max_length=20,  
        null = False,
        choices=Semester.choices,
        default=Semester.FIRST_SEMESTER
    )

    gwa = models.PositiveSmallIntegerField(null=True, blank=True)
    is_applying_for_merit = models.BooleanField(null=False, default=False)

    is_eligible = models.BooleanField(null=False, default=False)
    is_approved = models.BooleanField(null=False, default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    approved_by = models.ForeignKey(Officer, on_delete=models.CASCADE, null=True, blank=True)

    is_graduated = models.BooleanField(null=False, default=False)

    is_archived = models.BooleanField(null=False, default=False)