from django.db import models

from django.contrib.auth.models import (
    AbstractUser,
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission,
)
from django.db.models.query import QuerySet

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from datetime import date, datetime, timedelta

from demographics.models import Gender, ScholarshipType


class CustomUserManager(BaseUserManager):
    def create_user(self, email, role, password=None, **extra_fields):
        """Create, save and return a new user."""

        if not email:
            raise ValueError("Officer must have an email address.")
        if not role:
            raise ValueError("A role must be specified for the user.")

        # Normalize email addresses to lowercase for consistency
        email = self.normalize_email(email)

        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)

        # Set date_joined
        user.date_joined = timezone.now()

        # Generate formatted username
        user.username = user.generated_formatted_id()

        user.save(using=self.db)
        return user

    def create_superuser(self, email, role="ADMIN", password=None, **extra_fields):
        """Create, save, and return a new superuser."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Create the user
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        
        # Set date_joined
        user.date_joined = timezone.now()

        # Generate the formatted username
        user.username = user.generated_formatted_id()
        
        user.save(using=self._db)

        return user


class UserIdCounter(models.Model):
    counter = models.PositiveIntegerField(default=1)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        HEAD = "HEAD", "Head Officer"
        OFFICER = "OFFICER", "Officer"
        SCHOLAR = "SCHOLAR", "Scholar"

    # base_role = Role.ADMIN

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADMIN)
    username = models.CharField(_("username"), max_length=12, blank=True, unique=True)
    email = models.EmailField(_("email address"), blank=False, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def generate_unique_user_id(self):
        counter = UserIdCounter.objects.first()
        if counter is None:
            counter = UserIdCounter.objects.create(counter=1)
        
        user_id = counter.counter
        counter.counter += 1
        counter.save()
        return str(user_id).zfill(5)

    def generated_formatted_id(self):
        role_abbreviation = self.role[:1].upper()
        year_joined = str(self.date_joined.year)

        user_id = self.generate_unique_user_id()

        return f"{role_abbreviation}-{year_joined}-{user_id}"

    def save(self, *args, **kwargs):
        if not self.date_joined:
            self.date_joined = timezone.now()
        if not self.username:
            self.username = self.generated_formatted_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """
    Model that would serve as the storage of personal information for the registered users in the system.
    """
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

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='profile')

    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    middlename = models.CharField(max_length=30)

    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, default=3)
    
    contactnumber = models.CharField(max_length=11)
    
    house_address = models.CharField(max_length=50)
    barangay = models.CharField(max_length=50, null=True, choices=Barangay.choices)
    district = models.CharField(max_length=3, null=True, choices=District.choices, editable=False)

    birthdate = models.DateField(null=True, blank=False)

    def calculate_age(self):
        today = date.today()
        age = (
            today.year
            - self.birthdate.year
            - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        )
        return age
    
    def save(self, *args, **kwargs):
        # Automatically set the District based on the selected Barangay
        district_mapping = {
            UserProfile.Barangay.BAGUMBAYAN: UserProfile.District.ONE,
            UserProfile.Barangay.BAMBANG: UserProfile.District.ONE,
            UserProfile.Barangay.CALZADA: UserProfile.District.ONE,
            UserProfile.Barangay.HAGONOY: UserProfile.District.ONE,
            UserProfile.Barangay.IBAYO_TIPAS: UserProfile.District.ONE,
            UserProfile.Barangay.LIGID_TIPAS: UserProfile.District.ONE,
            UserProfile.Barangay.LOWER_BICUTAN: UserProfile.District.ONE,
            UserProfile.Barangay.NEW_LOWER_BICUTAN: UserProfile.District.ONE,
            UserProfile.Barangay.NAPINDAN: UserProfile.District.ONE,
            UserProfile.Barangay.PALINGON: UserProfile.District.ONE,
            UserProfile.Barangay.SAN_MIGUEL: UserProfile.District.ONE,
            UserProfile.Barangay.SANTA_ANA: UserProfile.District.ONE,
            UserProfile.Barangay.TUKTUKAN: UserProfile.District.ONE,
            UserProfile.Barangay.USUSAN: UserProfile.District.ONE,
            UserProfile.Barangay.WAWA: UserProfile.District.ONE,

            UserProfile.Barangay.BAGONG_TANYAG: UserProfile.District.TWO,
            UserProfile.Barangay.CENTRAL_BICUTAN: UserProfile.District.TWO,
            UserProfile.Barangay.CENTRAL_SIGNAL_VILLAGE: UserProfile.District.TWO,
            UserProfile.Barangay.FORT_BONIFACIO: UserProfile.District.TWO,
            UserProfile.Barangay.KATUPARAN: UserProfile.District.TWO,
            UserProfile.Barangay.MAHARLIKA_VILLAGE: UserProfile.District.TWO,
            UserProfile.Barangay.NORTH_DAANG_HARI: UserProfile.District.TWO,
            UserProfile.Barangay.NORTH_SIGNAL_VILLAGE: UserProfile.District.TWO,
            UserProfile.Barangay.PINAGSAMA: UserProfile.District.TWO,
            UserProfile.Barangay.SOUTH_DAANG_HARI: UserProfile.District.TWO,
            UserProfile.Barangay.SOUTH_SIGNAL_VILLAGE: UserProfile.District.TWO,
            UserProfile.Barangay.UPPER_BICUTAN: UserProfile.District.TWO,
            UserProfile.Barangay.WESTERN_BICUTAN: UserProfile.District.TWO,
        }

        self.district = district_mapping.get(self.barangay, self.district)
        super().save(*args, **kwargs)


"""
=================
    SCHOLAR
=================
"""
class ScholarManager(CustomUserManager):
    def get_queryset(self, **kwargs):
        results = super().get_queryset().filter(role=CustomUser.Role.SCHOLAR, **kwargs)

        return results

class ScholarManagerActive(models.Manager):
    def get_queryset(self, **kwargs):
        results = super(ScholarManagerActive, self).get_queryset().filter(is_active = True)

class ScholarManagerInactive(models.Manager):
    def get_queryset(self, **kwargs):
        results = super(ScholarManagerInactive, self).get_queryset().filter(is_active = False)


class Scholar(CustomUser):
    base_role = CustomUser.Role.SCHOLAR

    objects = ScholarManager()
    
    active = ScholarManagerActive()
    inactive = ScholarManagerInactive()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Scholars"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)
    
@receiver(post_save, sender=Scholar)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "SCHOLAR":
        ScholarProfile.objects.create(user=instance)


class ScholarProfile(UserProfile):

    religion = models.CharField(max_length=30, blank=True)
    facebook_link = models.CharField(max_length=100, blank=True)
    years_of_residency = models.PositiveSmallIntegerField(null=False, default=6)
    scholarship_type = models.ForeignKey(ScholarshipType, on_delete=models.CASCADE, null=False, default=5)

    # Determine if the applicant has already graduated
    is_graduated = models.BooleanField(null=False, default=False)                                        
    is_archived = models.BooleanField(null=False, default=False)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


"""
=================
    HEAD OFFICER
=================
"""
class HeadManager(BaseUserManager):
    def get_queryset(self, **kwargs):
        results = super().get_queryset().filter(role=CustomUser.Role.HEAD, **kwargs)

        return results

class HeadManagerActive(models.Manager):
    def get_queryset(self, **kwargs):
        results = super(HeadManagerActive, self).get_queryset().filter(is_active = True)

class HeadManagerInactive(models.Manager):
    def get_queryset(self, **kwargs):
        results = super(HeadManagerInactive, self).get_queryset().filter(is_active = False)

class Head(CustomUser):
    base_role = CustomUser.Role.HEAD

    objects = HeadManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Head Officers"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)

@receiver(post_save, sender=Head)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "HEAD":
        HeadProfile.objects.create(user=instance)


class HeadProfile(UserProfile):

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s Profile"
        return f"HeadProfile {self.id}"



"""
=================
    OFFICER
=================
"""
class OfficerManager(BaseUserManager):
    def get_queryset(self, **kwargs):
        results = super().get_queryset().filter(role=CustomUser.Role.OFFICER, **kwargs)

        return results

class OfficerManagerActive(models.Manager):
    def get_queryset(self, **kwargs):
        results = super(OfficerManagerActive, self).get_queryset().filter(is_active = True)

class OfficerManagerInactive(models.Manager):
    def get_queryset(self, **kwargs):
        results = super(OfficerManagerInactive, self).get_queryset().filter(is_active = False)

class Officer(CustomUser):
    base_role = CustomUser.Role.OFFICER

    objects = OfficerManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Officers"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)
    
@receiver(post_save, sender=Head)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "OFFICER":
        OfficerProfile.objects.create(user=instance)


class OfficerProfile(UserProfile):

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s Profile"
        return f"OfficerProfile {self.id}"