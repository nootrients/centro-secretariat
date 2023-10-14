from django.core.management.base import BaseCommand

from datetime import date

from demographics.models import Applicant, Gender


class Command(BaseCommand):
    help = "Add Applicant records to the database"

    def handle(self, *args, **options):
        birthdate = date(1998, 1, 18)

        gender_instance = Gender.objects.get(id=1)

        # Your code to create Gender records goes here
        Applicant.objects.create(
            firstname="Patrick",
            lastname="Villanueva",
            middlename="Librilla",
            gender=gender_instance,
            contactnumber="+639268868211",
            house_address="Blk. 10 Lt. 11 St. Jude Street",
            barangay="Central Signal Village",
            district="2",
            religion="Catholic",
            facebookLink="www.facebook.com/testData1",
            email="pvillanueva@email.com",
            yearsOfResidency=24,
            birthdate=birthdate,
        )

        self.stdout.write(self.style.SUCCESS("Successfully added Applicant records"))
