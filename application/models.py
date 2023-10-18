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
    class Religion(models.TextChoices):
        ROMAN_CATHOLIC = "ROMAN CATHOLIC", "ROMAN CATHOLIC"
        PROTESTANT = "PROTESTANT", "PROTESTANT"
        BAPTIST = "BAPTIST", "BAPTIST"
        IGLESIA_NI_CRISTO = "IGLESIA NI CRISTO", "IGLESIA NI CRISTO"
        ISLAM = "ISLAM", "ISLAM"
        EVANGELICAL_CHRISTIAN = "EVANGELICAL CHRISTIAN", "EVANGELICAL CHRISTIAN"

    
    class ScholarshipType(models.TextChoices):
        BASIC_PLUS_SUC = "BASIC PLUS SUC", "BASIC PLUS SUC"
        SUC_LCU = "SUC_LCU", "SUC/LCU"
        BASIC_SCHOLARSHIP = "BASIC SCHOLARSHIP", "BASIC SCHOLARSHIP"
        HONORS = "HONORS", "HONORS (FULL)"
        PRIORITY = "PRIORITY", "PRIORITY"
        PREMIER = "PREMIER", "PREMIER"


    class Semester(models.TextChoices):
        FIRST_SEMESTER = "FIRST SEMESTER", "FIRST SEMESTER"
        SECOND_SEMESTER = "SECOND SEMESTER", "SECOND SEMESTER"


    class ApplicantStatus(models.TextChoices):
        NEW_APPLICANT = "NEW APPLICANT", "NEW APPLICANT"
        RENEWING_APPLICANT = "RENEWING APPLICANT", "RENEWING APPLICANT"


    class YearLevel(models.TextChoices):
        FIRST_YEAR = "FIRST YEAR", "FIRST YEAR"
        SECOND_YEAR = "SECOND YEAR", "SECOND YEAR"
        THIRD_YEAR = "THIRD YEAR", "THIRD YEAR"
        FOURTH_YEAR = "FOURTH YEAR", "FOURTH YEAR"
        FIFTH_YEAR = "FIFTH YEAR", "FIFTH YEAR"

    
    class CourseDuration(models.TextChoices):
        THREE_YEARS = "THREE YEARS", "THREE (3) YEARS"
        FOUR_YEARS = "FOUR YEARS", "FOUR (4) YEARS"
        FIVE_YEARS = "FIVE YEARS", "FIVE (5) YEARS"
    

    application_uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)


    """
    PERSONAL INFORMATION SECTION
    """
    national_id = models.ImageField(upload_to='uploads/images',null=False,blank=False)
    
    # These fields are not editable
    firstname = models.CharField(max_length=30, null=False, blank=False)           # Auto generated from the scanned National ID
    lastname = models.CharField(max_length=30, null=False, blank=False)            # Auto generated from the scanned National ID
    middlename = models.CharField(max_length=30, null=False, blank=False)          # Auto generated from the scanned National ID
    
    gender = models.CharField(null=False, )                                        # Auto generated from the scanned National ID

    birthdate = models.DateField(null=True, blank=False)                           # Auto generated from the scanned National ID (?????)
    
    house_address = models.CharField(max_length=50)
    # barangay = models.CharField(max_length=50, null=True, choices=Barangay.choices)           # Possible duplicate value on UserProfile model
    # district = models.CharField(max_length=3, null=True, choices=District.choices)            # Possible duplicate value on UserProfile model
    
    email_address = models.EmailField(unique=True, blank=False)
    personalized_facebook_link = models.CharField(max_length=30, null=False, blank=False)

    religion = models.CharField(max_length=30, choices=Religion.choices,null=False, blank=False)

    """
    APPLICATION VALIDATION SECTION
    """
    applicant_status = models.CharField(max_length=18, choices=ApplicantStatus.choices, null=False, blank=False)
    scholarship_type = models.CharField(max_length=20, choices=ScholarshipType.choices, null = False, default=ScholarshipType.BASIC_SCHOLARSHIP, blank=False)
    
    academic_year = AcademicYearField()
    semester = models.CharField(max_length=20, null=False, choices=Semester.choices, default=Semester.FIRST_SEMESTER, blank=False)

    informative_copy_of_grades = models.FileField(upload_to='uploads/pdfs', null=False, blank=False)
    is_applying_for_merit = models.BooleanField(null=False, default=False, blank=False)                 # (SWA at least 1.75 equivalent to 88.75%) || Get Informative Copy of Grades > 
    
    years_of_residency = models.PositiveSmallIntegerField(null=False, blank=False)                      # In Taguig City


    """
    CURRENT EDUCATION SECTION    
    """
    university_attending = models.CharField(max_length=40, null=False, blank=False)                         # REFERENCE TO ANOTHER TABLE
    course_taking = models.CharField(max_length=40, null=False, blank=False)                                # REFERENCE TO ANOTHER TABLE
    year_level = models.CharField(max_length=15, choices=YearLevel.choices, null=False, blank=False)
    is_graduating = models.BooleanField(null=False, blank=False, default=False)
    course_duration = models.CharField(max_length=15, choices=CourseDuration.choices, null=False, blank=False)

    
    """
    EDUCATIONAL BACKGROUND
    """
    # CONTINUE
    # HAVE IT ON ANOTHER MODEL
    
    # Fill table on PartneredUniversities
    # Fill table on Courses

    """
    UTILITIES SECTION
    """
    is_eligible = models.BooleanField(null=False, default=False)
    is_approved = models.BooleanField(null=False, default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    approved_by = models.ForeignKey(Officer, on_delete=models.CASCADE, null=True, blank=True)

    # Transfer to ScholarProfile instead
    # Determine if the applicant has already graduated
    is_graduated = models.BooleanField(null=False, default=False)                                        
    is_archived = models.BooleanField(null=False, default=False)

    def calculate_age(self):
        today = date.today()
        age = (
            today.year
            - self.birthdate.year
            - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        )
        return age

    def __str__(self):
        return self.application_uuid
    

class PartneredUniversities(models.Model):
    university_name = models.CharField(max_length=50, null=False, blank=False)


class Courses(models.Model):
    course_name = models.CharField(max_length=50, null=False, blank=False)