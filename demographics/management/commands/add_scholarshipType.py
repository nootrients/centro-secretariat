from django.core.management.base import BaseCommand

from demographics.models import ScholarshipType


class Command(BaseCommand):
    help = "Add Scholarship Type records to the database"

    def handle(self, *args, **options):
        # Your code to create ScholarshipType records goes here
        ScholarshipType.objects.create(scholarship_name="Honors")
        ScholarshipType.objects.create(scholarship_name="Premier")
        ScholarshipType.objects.create(scholarship_name="Priority")
        ScholarshipType.objects.create(scholarship_name="Basic Plus")
        ScholarshipType.objects.create(scholarship_name="Basic")
        ScholarshipType.objects.create(scholarship_name="SUC/LCU")
        ScholarshipType.objects.create(scholarship_name="Review")
        ScholarshipType.objects.create(scholarship_name="Lead")

        self.stdout.write(
            self.style.SUCCESS("Successfully added Scholarship Type records")
        )
