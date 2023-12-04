from django.db import models
from django.utils import timezone

from accounts.models import Officer, Scholar
from demographics.models import Gender

from datetime import date, datetime

# Create your models here.
class AcademicYearField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 9
        kwargs['editable'] = False
        kwargs['default'] = self.calculate_academic_year
        super().__init__(*args, **kwargs)

    def calculate_academic_year(self):
        today = date.today()
        current_year = today.year
        next_year = current_year + 1

        return f"{current_year}-{next_year}"


class PartneredUniversities(models.Model):
    university_name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.university_name


class Courses(models.Model):
    course_name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.course_name
    

class TempApplicationIdCounter(models.Model):
    counter = models.PositiveIntegerField(default=1)


class Applications(models.Model):
    class Barangay(models.TextChoices):
        """
        DISTRICT 1
        """
        BAGUMBAYAN = "BAGUMBAYAN", "Bagumbayan"
        BAMBANG = "BAMBANG", "Bambang"
        CALZADA = "CALZADA", "Calzada"
        HAGONOY = "HAGONOY", "Hagonoy"
        IBAYO_TIPAS = "IBAYO TIPAS", "Ibayo Tipas"
        LIGID_TIPAS = "LIGID TIPAS", "Ligid Tipas"
        LOWER_BICUTAN = "LOWER BICUTAN", "Lower Bicutan"
        NEW_LOWER_BICUTAN = "NEW LOWER BICUTAN", "New Lower Bicutan"
        NAPINDAN = "NAPINDAN", "Napindan"
        PALINGON = "PALINGON", "Palingon"
        SAN_MIGUEL = "SAN MIGUEL", "San Miguel"
        SANTA_ANA = "SANTA ANA", "Santa Ana"
        TUKTUKAN = "TUKTUKAN", "Tuktukan"
        USUSAN = "USUSAN", "Ususan"
        WAWA = "WAWA", "Wawa"


        """
        DISTRICT 2
        """
        BAGONG_TANYAG = "BAGONG TANYAG", "Bagong Tanyag"
        CENTRAL_BICUTAN = "CENTRAL BICUTAN", "Central Bicutan"
        CENTRAL_SIGNAL_VILLAGE = "CENTRAL SIGNAL VILLAGE", "Central Signal Village"
        FORT_BONIFACIO = "FORT BONIFACIO", "Fort Bonifacio"
        KATUPARAN = "KATUPARAN", "Katuparan"
        MAHARLIKA_VILLAGE = "MAHARLIKA VILLAGE", "Maharlika Village"
        NORTH_DAANG_HARI = "NORTH DAANG_HARI", "North Daang Hari"
        NORTH_SIGNAL_VILLAGE = "NORTH SIGNAL VILLAGE", "North Signal Village"
        PINAGSAMA = "PINAGSAMA", "Pinagsama"
        SOUTH_DAANG_HARI = "SOUTH DAANG HARI", "South Daang Hari"
        SOUTH_SIGNAL_VILLAGE = "SOUTH SIGNAL VILLAGE", "South Signal Village"
        UPPER_BICUTAN = "UPPER BICUTAN", "Upper Bicutan"
        WESTERN_BICUTAN = "WESTERN BICUTAN", "Western Bicutan"

    class District(models.TextChoices):
        ONE = "ONE", "1"
        TWO = "TWO", "2"

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


    class SchoolType(models.TextChoices):
        PRIVATE = "PRIVATE", "PRIVATE"
        PUBLIC = "PUBLIC", "PUBLIC"


    class StudentStatus(models.TextChoices):
        REGULAR = "REGULAR", "REGULAR"
        IRREGULAR = "IRREGULAR", "IRREGULAR"
        OCTOBERIAN = "OCTOBERIAN", "OCTOBERIAN"


    class Status(models.TextChoices):
        PENDING = "PENDING", "PENDING"
        ACCEPTED = "ACCEPTED", "ACCEPTED"
        REJECTED = "REJECTED", "REJECTED"

    
    # Generate from front-end
    application_reference_id = models.CharField(max_length=20, null=True, blank=False)

#PERSONAL INFORMATION SECTION
    national_id = models.ImageField(upload_to='final/applicant/ids', null=True, blank=False)
    
    # Auto generated from the scanned National ID
    lastname = models.CharField(max_length=30, null=True, blank=True, default="Unable to extract from image.")
    firstname = models.CharField(max_length=30, null=True, blank=True, default="Unable to extract from image.")
    middlename = models.CharField(max_length=30, null=True, blank=True, default="Unable to extract from image.")          
    
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, null=True, blank=False)                                    

    birthdate = models.DateField(null=True, blank=False)
    
    house_address = models.TextField(max_length=50, null=True, blank=False)
    barangay = models.CharField(max_length=50, null=True, choices=Barangay.choices)           # Possible duplicate value on UserProfile model
    district = models.CharField(max_length=3, null=True, choices=District.choices)            # Editable = False || Auto-fill based on Barangay's value
    
    email_address = models.EmailField(unique=True, null=True, blank=False)
    personalized_facebook_link = models.CharField(max_length=30, null=True, blank=False)

    religion = models.CharField(max_length=30, choices=Religion.choices, null=True, blank=False)



#APPLICATION VALIDATION SECTION
    applicant_status = models.CharField(max_length=18, choices=ApplicantStatus.choices, null=True, default=ApplicantStatus.NEW_APPLICANT, blank=False)
    scholarship_type = models.CharField(max_length=20, 
                                        choices=ScholarshipType.choices, 
                                        null=True, 
                                        default=ScholarshipType.BASIC_SCHOLARSHIP, 
                                        blank=False,
                                        help_text='Kindly refer to the guidelines. Fraudulent inputs will deem your application as void.'
                                        )

    applying_for_academic_year = AcademicYearField()
    semester = models.CharField(max_length=20, null=True, choices=Semester.choices, default=Semester.FIRST_SEMESTER, blank=False)

    informative_copy_of_grades = models.FileField(upload_to='final/applicant/icg', null=True, blank=False)
    is_applying_for_merit = models.BooleanField(null=False, default=False, blank=False, help_text='SWA at least 1.75 equivalent to 88.75%).')

    voter_certificate = models.FileField(upload_to='final/applicant/voters_certificate', null=True, blank=False)
    
    # Auto generated from the scanned Voter's Certificate
    years_of_residency = models.CharField(max_length = 30, null=True, blank=False)
    voters_issued_at = models.CharField(max_length=70, null=True, blank=True)
    voters_issuance_date = models.CharField(max_length=70, null=True, blank=True)

    
# CURRENT EDUCATION SECTION    
    university_attending = models.ForeignKey(PartneredUniversities, on_delete=models.CASCADE, max_length=40, null=True, blank=False)
    registration_form = models.FileField(upload_to='final/applicant/registration_form', null=True, blank=False, help_text="Insert your Registration/Enrollment Form for the current semester.")
    total_units_enrolled = models.PositiveSmallIntegerField(null=True, blank=False)
    is_ladderized = models.BooleanField(null=True, blank=False)
    course_taking = models.ForeignKey(Courses, on_delete=models.CASCADE, max_length=50, null=True, blank=False)
    year_level = models.CharField(max_length=15, choices=YearLevel.choices, null=True, blank=False)
    is_graduating = models.BooleanField(null=False, blank=False, default=False)
    course_duration = models.CharField(max_length=15, choices=CourseDuration.choices, null=True, blank=False)
    

# EDUCATIONAL BACKGROUND
    # Elementary
    elementary_school = models.CharField(max_length=50, null=True, blank=False)
    elementary_school_type = models.CharField(max_length=10, choices=SchoolType.choices, null=True, blank=False)
    elementary_school_address = models.TextField(max_length=100, null=True, blank=False)
    elementary_start_end = models.CharField(max_length=9, null=True, blank=False)

    # Junior HS
    jhs_school = models.CharField(max_length=50, null=True, blank=False)
    jhs_school_type = models.CharField(max_length=10, choices=SchoolType.choices, null=True, blank=False)
    jhs_school_address = models.TextField(max_length=100, null=True, blank=False)
    jhs_start_end = models.CharField(max_length=9, null=True, blank=False)
    
    # Senior HS
    shs_school = models.CharField(max_length=50, null=True, blank=False)
    shs_school_type = models.CharField(max_length=10, choices=SchoolType.choices, null=True, blank=False)
    shs_school_address = models.TextField(max_length=100, null=True, blank=False)
    shs_start_end = models.CharField(max_length=9, null=True, blank=False)


#GUARDIAN'S BACKGROUND
    guardian_complete_name = models.CharField(max_length=50, null=True, blank=False)
    guardian_complete_address = models.TextField(max_length=100, null=True, blank=False)
    guardian_contact_number = models.CharField(max_length=11, null=True, blank=False)
    guardian_occupation = models.CharField(max_length=30, null=True, blank=False)
    guardian_place_of_work = models.TextField(max_length=30, null=True, blank=False)
    guardian_educational_attainment = models.CharField(max_length=30, null=True, blank=False)

    guardians_voter_certificate = models.FileField(upload_to='final/guardian/voters_certificate', null=True, blank=False, help_text="Insert your SCANNED COPY (IMG) guardian's voter certificate (for verification and validation purposes).")
    guardians_years_of_residency = models.CharField(max_length = 30, null=True, blank=False)
    guardians_voters_issued_at = models.CharField(max_length=70, null=True, blank=False)
    guardians_voters_issuance_date = models.CharField(max_length=70, null=True, blank=False)

# MISCELLANEOUS INFORMATION
    number_of_semesters_before_graduating = models.PositiveSmallIntegerField(null=True, blank=False)
    transferee = models.CharField(max_length=50, null=True, default='N/A', blank=False, help_text="Name of your previous school/university.")
    shiftee = models.CharField(max_length=30, null=True, default='N/A', blank=False, help_text="Title of your previous course (if shiftee).")
    student_status = models.CharField(max_length=20, choices=StudentStatus.choices, null=True, blank=False)
    

# UTILITIES SECTION
    is_eligible = models.BooleanField(null=False, default=False)
    expires_at = models.DateTimeField(null=True, blank=False)

    # is_approved = models.BooleanField(null=False, default=False)
    application_status = models.CharField(max_length=50, null=True, blank=False, choices=Status.choices, default=Status.PENDING)
    evaluated_by = models.ForeignKey(Officer, on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # To be filled up after approval
    scholar = models.OneToOneField(Scholar, on_delete=models.CASCADE, null=True, blank=True, related_name='scholar')

    @property
    def calculate_age(self):
        today = date.today()
        age = (
            today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        )
        return age

    def save(self, *args, **kwargs):
        # Automatically set the District based on the selected Barangay
        district_mapping = {
            Applications.Barangay.BAGUMBAYAN: Applications.District.ONE,
            Applications.Barangay.BAMBANG: Applications.District.ONE,
            Applications.Barangay.CALZADA: Applications.District.ONE,
            Applications.Barangay.HAGONOY: Applications.District.ONE,
            Applications.Barangay.IBAYO_TIPAS: Applications.District.ONE,
            Applications.Barangay.LIGID_TIPAS: Applications.District.ONE,
            Applications.Barangay.LOWER_BICUTAN: Applications.District.ONE,
            Applications.Barangay.NEW_LOWER_BICUTAN: Applications.District.ONE,
            Applications.Barangay.NAPINDAN: Applications.District.ONE,
            Applications.Barangay.PALINGON: Applications.District.ONE,
            Applications.Barangay.SAN_MIGUEL: Applications.District.ONE,
            Applications.Barangay.SANTA_ANA: Applications.District.ONE,
            Applications.Barangay.TUKTUKAN: Applications.District.ONE,
            Applications.Barangay.USUSAN: Applications.District.ONE,
            Applications.Barangay.WAWA: Applications.District.ONE,

            Applications.Barangay.BAGONG_TANYAG: Applications.District.TWO,
            Applications.Barangay.CENTRAL_BICUTAN: Applications.District.TWO,
            Applications.Barangay.CENTRAL_SIGNAL_VILLAGE: Applications.District.TWO,
            Applications.Barangay.FORT_BONIFACIO: Applications.District.TWO,
            Applications.Barangay.KATUPARAN: Applications.District.TWO,
            Applications.Barangay.MAHARLIKA_VILLAGE: Applications.District.TWO,
            Applications.Barangay.NORTH_DAANG_HARI: Applications.District.TWO,
            Applications.Barangay.NORTH_SIGNAL_VILLAGE: Applications.District.TWO,
            Applications.Barangay.PINAGSAMA: Applications.District.TWO,
            Applications.Barangay.SOUTH_DAANG_HARI: Applications.District.TWO,
            Applications.Barangay.SOUTH_SIGNAL_VILLAGE: Applications.District.TWO,
            Applications.Barangay.UPPER_BICUTAN: Applications.District.TWO,
            Applications.Barangay.WESTERN_BICUTAN: Applications.District.TWO,
        }

        # Set expires_at when is_eligible is set to False
        if not self.is_eligible:
            self.expires_at = timezone.now() + timezone.timedelta(days=3)
        else:
            # Clear expires_at when is_eligible is set to True
            self.expires_at = None

        self.district = district_mapping.get(self.barangay, self.district)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete associated files
        for file_field in self._meta.fields:
            if isinstance(file_field, models.FileField):
                file = getattr(self, file_field.name)
                if file:
                    # Assuming you're using the default storage
                    if file.storage.exists(file.name):
                        file.storage.delete(file.name)

        # Call the parent class's delete method to delete the database record
        super(Applications, self).delete(*args, **kwargs)

    def __str__(self):
        return self.application_reference_id

class EligibilityConfig(models.Model):
    class Semester(models.TextChoices):
        FIRST_SEMESTER = "FIRST SEMESTER", "FIRST SEMESTER"
        SECOND_SEMESTER = "SECOND SEMESTER", "SECOND SEMESTER"
    
    applying_for_academic_year = AcademicYearField()
    semester = models.CharField(max_length=50, null=False, blank=False, choices=Semester.choices, default=Semester.FIRST_SEMESTER)
    
    minimum_residency = models.PositiveSmallIntegerField(null=False, blank=False, default=3)
    guardians_minimum_residency = models.PositiveSmallIntegerField(null=False, blank=False, default=3)
    
    voters_validity_year_start = models.PositiveSmallIntegerField(null=True, blank=False)
    voters_validity_year_end = models.PositiveSmallIntegerField(null=True, blank=False)

    is_ongoing = models.BooleanField(null=True, blank=False)


class TempApplications(models.Model):
    class Barangay(models.TextChoices):
        """
        DISTRICT 1
        """
        BAGUMBAYAN = "BAGUMBAYAN", "Bagumbayan"
        BAMBANG = "BAMBANG", "Bambang"
        CALZADA = "CALZADA", "Calzada"
        HAGONOY = "HAGONOY", "Hagonoy"
        IBAYO_TIPAS = "IBAYO TIPAS", "Ibayo Tipas"
        LIGID_TIPAS = "LIGID TIPAS", "Ligid Tipas"
        LOWER_BICUTAN = "LOWER BICUTAN", "Lower Bicutan"
        NEW_LOWER_BICUTAN = "NEW LOWER BICUTAN", "New Lower Bicutan"
        NAPINDAN = "NAPINDAN", "Napindan"
        PALINGON = "PALINGON", "Palingon"
        SAN_MIGUEL = "SAN MIGUEL", "San Miguel"
        SANTA_ANA = "SANTA ANA", "Santa Ana"
        TUKTUKAN = "TUKTUKAN", "Tuktukan"
        USUSAN = "USUSAN", "Ususan"
        WAWA = "WAWA", "Wawa"


        """
        DISTRICT 2
        """
        BAGONG_TANYAG = "BAGONG TANYAG", "Bagong Tanyag"
        CENTRAL_BICUTAN = "CENTRAL BICUTAN", "Central Bicutan"
        CENTRAL_SIGNAL_VILLAGE = "CENTRAL SIGNAL VILLAGE", "Central Signal Village"
        FORT_BONIFACIO = "FORT BONIFACIO", "Fort Bonifacio"
        KATUPARAN = "KATUPARAN", "Katuparan"
        MAHARLIKA_VILLAGE = "MAHARLIKA VILLAGE", "Maharlika Village"
        NORTH_DAANG_HARI = "NORTH DAANG_HARI", "North Daang Hari"
        NORTH_SIGNAL_VILLAGE = "NORTH SIGNAL VILLAGE", "North Signal Village"
        PINAGSAMA = "PINAGSAMA", "Pinagsama"
        SOUTH_DAANG_HARI = "SOUTH DAANG HARI", "South Daang Hari"
        SOUTH_SIGNAL_VILLAGE = "SOUTH SIGNAL VILLAGE", "South Signal Village"
        UPPER_BICUTAN = "UPPER BICUTAN", "Upper Bicutan"
        WESTERN_BICUTAN = "WESTERN BICUTAN", "Western Bicutan"

    class District(models.TextChoices):
        ONE = "ONE", "1"
        TWO = "TWO", "2"

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


    class SchoolType(models.TextChoices):
        PRIVATE = "PRIVATE", "PRIVATE"
        PUBLIC = "PUBLIC", "PUBLIC"


    class StudentStatus(models.TextChoices):
        REGULAR = "REGULAR", "REGULAR"
        IRREGULAR = "IRREGULAR", "IRREGULAR"
        OCTOBERIAN = "OCTOBERIAN", "OCTOBERIAN"
    
    # Generate from front-end
    application_reference_id = models.CharField(max_length=20, null=True, blank=False)

#PERSONAL INFORMATION SECTION
    national_id = models.ImageField(upload_to='tmp/applicant/ids', null=True, blank=False)
    
    # Auto generated from the scanned National ID
    lastname = models.CharField(max_length=30, null=True, blank=True, default="Unable to extract from image.")
    firstname = models.CharField(max_length=30, null=True, blank=True, default="Unable to extract from image.")
    middlename = models.CharField(max_length=30, null=True, blank=True, default="Unable to extract from image.")          
    
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, null=True, blank=False)                                    

    birthdate = models.DateField(null=True, blank=False)
    
    house_address = models.TextField(max_length=50, null=True, blank=False)
    barangay = models.CharField(max_length=50, null=True, choices=Barangay.choices)           # Possible duplicate value on UserProfile model
    district = models.CharField(max_length=3, null=True, choices=District.choices)            # Editable = False || Auto-fill based on Barangay's value
    
    email_address = models.EmailField(unique=True, null=True, blank=False)
    personalized_facebook_link = models.CharField(max_length=30, null=True, blank=False)

    religion = models.CharField(max_length=30, choices=Religion.choices, null=True, blank=False)



#APPLICATION VALIDATION SECTION
    applicant_status = models.CharField(max_length=18, choices=ApplicantStatus.choices, null=True, default=ApplicantStatus.NEW_APPLICANT, blank=False)
    scholarship_type = models.CharField(max_length=20, 
                                        choices=ScholarshipType.choices, 
                                        null=True, 
                                        default=ScholarshipType.BASIC_SCHOLARSHIP, 
                                        blank=False,
                                        help_text='Kindly refer to the guidelines. Fraudulent inputs will deem your application as void.'
                                        )

    applying_for_academic_year = AcademicYearField()
    semester = models.CharField(max_length=20, null=True, choices=Semester.choices, default=Semester.FIRST_SEMESTER, blank=False)

    informative_copy_of_grades = models.FileField(upload_to='tmp/applicant/icg', null=True, blank=False)
    is_applying_for_merit = models.BooleanField(null=False, default=False, blank=False, help_text='SWA at least 1.75 equivalent to 88.75%).')

    voter_certificate = models.FileField(upload_to='tmp/applicant/voters_certificate', null=True, blank=False)
    
    # Auto generated from the scanned Voter's Certificate
    years_of_residency = models.CharField(max_length = 30, null=True, blank=False)
    voters_issued_at = models.CharField(max_length=70, null=True, blank=True)
    voters_issuance_date = models.CharField(max_length=70, null=True, blank=True)

    
# CURRENT EDUCATION SECTION    
    university_attending = models.ForeignKey(PartneredUniversities, on_delete=models.CASCADE, max_length=40, null=True, blank=False)
    registration_form = models.FileField(upload_to='tmp/applicant/registration_form', null=True, blank=False, help_text="Insert your Registration/Enrollment Form for the current semester.")
    total_units_enrolled = models.PositiveSmallIntegerField(null=True, blank=False)
    is_ladderized = models.BooleanField(null=True, blank=False)
    course_taking = models.ForeignKey(Courses, on_delete=models.CASCADE, max_length=50, null=True, blank=False)
    year_level = models.CharField(max_length=15, choices=YearLevel.choices, null=True, blank=False)
    is_graduating = models.BooleanField(null=False, blank=False, default=False)
    course_duration = models.CharField(max_length=15, choices=CourseDuration.choices, null=True, blank=False)
    

# EDUCATIONAL BACKGROUND
    # Elementary
    elementary_school = models.CharField(max_length=50, null=True, blank=False)
    elementary_school_type = models.CharField(max_length=10, choices=SchoolType.choices, null=True, blank=False)
    elementary_school_address = models.TextField(max_length=100, null=True, blank=False)
    elementary_start_end = models.CharField(max_length=9, null=True, blank=False)

    # Junior HS
    jhs_school = models.CharField(max_length=50, null=True, blank=False)
    jhs_school_type = models.CharField(max_length=10, choices=SchoolType.choices, null=True, blank=False)
    jhs_school_address = models.TextField(max_length=100, null=True, blank=False)
    jhs_start_end = models.CharField(max_length=9, null=True, blank=False)
    
    # Senior HS
    shs_school = models.CharField(max_length=50, null=True, blank=False)
    shs_school_type = models.CharField(max_length=10, choices=SchoolType.choices, null=True, blank=False)
    shs_school_address = models.TextField(max_length=100, null=True, blank=False)
    shs_start_end = models.CharField(max_length=9, null=True, blank=False)


#GUARDIAN'S BACKGROUND
    guardian_complete_name = models.CharField(max_length=50, null=True, blank=False)
    guardian_complete_address = models.TextField(max_length=100, null=True, blank=False)
    guardian_contact_number = models.CharField(max_length=11, null=True, blank=False)
    guardian_occupation = models.CharField(max_length=30, null=True, blank=False)
    guardian_place_of_work = models.TextField(max_length=30, null=True, blank=False)
    guardian_educational_attainment = models.CharField(max_length=30, null=True, blank=False)

    guardians_voter_certificate = models.FileField(upload_to='tmp/guardian/voters_certificate', null=True, blank=False, help_text="Insert your SCANNED COPY (IMG) guardian's voter certificate (for verification and validation purposes).")
    guardians_years_of_residency = models.CharField(max_length = 30, null=True, blank=False)
    guardians_voters_issued_at = models.CharField(max_length=70, null=True, blank=False)
    guardians_voters_issuance_date = models.CharField(max_length=70, null=True, blank=False)

# MISCELLANEOUS INFORMATION
    number_of_semesters_before_graduating = models.PositiveSmallIntegerField(null=True, blank=False)
    transferee = models.CharField(max_length=50, null=True, default='N/A', blank=False, help_text="Name of your previous school/university.")
    shiftee = models.CharField(max_length=30, null=True, default='N/A', blank=False, help_text="Title of your previous course (if shiftee).")
    student_status = models.CharField(max_length=20, choices=StudentStatus.choices, null=True, blank=False)

    @property
    def calculate_age(self):
        today = date.today()
        age = (
            today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        )
        return age

    def save(self, *args, **kwargs):
        # Automatically set the District based on the selected Barangay
        district_mapping = {
            Applications.Barangay.BAGUMBAYAN: Applications.District.ONE,
            Applications.Barangay.BAMBANG: Applications.District.ONE,
            Applications.Barangay.CALZADA: Applications.District.ONE,
            Applications.Barangay.HAGONOY: Applications.District.ONE,
            Applications.Barangay.IBAYO_TIPAS: Applications.District.ONE,
            Applications.Barangay.LIGID_TIPAS: Applications.District.ONE,
            Applications.Barangay.LOWER_BICUTAN: Applications.District.ONE,
            Applications.Barangay.NEW_LOWER_BICUTAN: Applications.District.ONE,
            Applications.Barangay.NAPINDAN: Applications.District.ONE,
            Applications.Barangay.PALINGON: Applications.District.ONE,
            Applications.Barangay.SAN_MIGUEL: Applications.District.ONE,
            Applications.Barangay.SANTA_ANA: Applications.District.ONE,
            Applications.Barangay.TUKTUKAN: Applications.District.ONE,
            Applications.Barangay.USUSAN: Applications.District.ONE,
            Applications.Barangay.WAWA: Applications.District.ONE,

            Applications.Barangay.BAGONG_TANYAG: Applications.District.TWO,
            Applications.Barangay.CENTRAL_BICUTAN: Applications.District.TWO,
            Applications.Barangay.CENTRAL_SIGNAL_VILLAGE: Applications.District.TWO,
            Applications.Barangay.FORT_BONIFACIO: Applications.District.TWO,
            Applications.Barangay.KATUPARAN: Applications.District.TWO,
            Applications.Barangay.MAHARLIKA_VILLAGE: Applications.District.TWO,
            Applications.Barangay.NORTH_DAANG_HARI: Applications.District.TWO,
            Applications.Barangay.NORTH_SIGNAL_VILLAGE: Applications.District.TWO,
            Applications.Barangay.PINAGSAMA: Applications.District.TWO,
            Applications.Barangay.SOUTH_DAANG_HARI: Applications.District.TWO,
            Applications.Barangay.SOUTH_SIGNAL_VILLAGE: Applications.District.TWO,
            Applications.Barangay.UPPER_BICUTAN: Applications.District.TWO,
            Applications.Barangay.WESTERN_BICUTAN: Applications.District.TWO,
        }

        self.district = district_mapping.get(self.barangay, self.district)

        if not self.application_reference_id:
            # Generate the application_reference_id if not already set
            self.application_reference_id = self.generate_application_reference_id()

        super().save(*args, **kwargs)

    def generate_application_reference_id(self):
        print(f"Debug: self.scholarship_type = {self.scholarship_type}")
        print(f"Debug: self.pk = {self.pk}")
        
        # Map scholarship type strings to numerical values
        scholarship_type_mapping = {
            "BASIC PLUS SUC": "0",
            "SUC_LCU": "1",
            "BASIC SCHOLARSHIP": "2",
            "HONORS": "3",
            "PRIORITY": "4",
            "PREMIER": "5",
        }

        # Get the numeric value of the scholarship type with a default of "UNKNOWN"
        scholarship_type_numeric = scholarship_type_mapping.get(self.scholarship_type, "UNKNOWN")

        if scholarship_type_numeric is None:
            print(f"Warning: Unknown scholarship type encountered - {self.scholarship_type}")

        # Increment the counter and create the new application_reference_id
        counter = TempApplicationIdCounter.objects.first()
        if counter is None:
            counter = TempApplicationIdCounter.objects.create()

        counter.counter += 1
        counter.save(update_fields=['counter'])

        # Create the new application_reference_id
        return f"{datetime.now().year:04d}-{counter.counter:05d}-ST-{scholarship_type_numeric}"

    def delete(self, *args, **kwargs):
        # Delete associated files
        for file_field in self._meta.fields:
            if isinstance(file_field, models.FileField):
                file = getattr(self, file_field.name)
                if file:
                    # Assuming you're using the default storage
                    if file.storage.exists(file.name):
                        file.storage.delete(file.name)

        # Call the parent class's delete method to delete the database record
        super(TempApplications, self).delete(*args, **kwargs)

    def __str__(self):
        return self.application_reference_id
    

class StatusUpdate(models.Model):
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, null=True)
    application_reference_id = models.CharField(max_length=100, null=True, blank=False)
    date_accomplished = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=150, null=True, blank=False)
    current_step = models.PositiveSmallIntegerField(null=True, blank=False, default=1)
    is_active = models.BooleanField(default=False, blank=False)


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('ACCEPTED', 'ACCEPTED'),
        ('REJECTED', 'REJECTED'),
    ]

    application_id = models.ForeignKey(Applications, on_delete=models.CASCADE)
    officer = models.ForeignKey(Officer, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)