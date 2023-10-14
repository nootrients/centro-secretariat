from django.core.management.base import BaseCommand

from datetime import date

from accounts.models import ScholarProfile, CustomUser
from demographics.models import Gender, ScholarshipType

class Command(BaseCommand):
    help = "Add Applicant records to the database"

    def handle(self, *args, **options):
        user = CustomUser.objects.get(email='scholar_1@email.com')
        
        birthdate = date(2000, 12, 13)

        gender_instance = Gender.objects.get(id=1)

        scholarship_type_instance = ScholarshipType.objects.get(id=4)

        # Your code to create Gender records goes here
        ScholarProfile.objects.create(
            user=user,
            firstname="Brian",
            lastname="Villanueva",
            middlename="Librilla",
            
            gender=gender_instance,
            
            contactnumber="+639268757100",
            
            house_address="Blk. 10 Lt. 11 St. Jude Street",
            barangay="Central Signal Village",
            district="2",
            
            religion="Catholic",
            
            facebook_link="www.facebook.com/OevnaXZ",
            
            years_of_Residency=22,
            
            birthdate=birthdate,

            scholarship_type=scholarship_type_instance,
        )

        self.stdout.write(self.style.SUCCESS("Successfully added Scholar Profile records"))