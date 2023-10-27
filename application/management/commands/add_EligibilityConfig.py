from django.core.management.base import BaseCommand

from datetime import date

from application.models import EligibilityConfig, AcademicYearField, Applications


class Command(BaseCommand):
    help = "Set Eligibility Configuration to use as constraints for the automated eligibility checking."

    def handle(self, *args, **options):

        # Your code to set constraints for eligibility goes here
        EligibilityConfig.objects.create(
            academic_year=AcademicYearField,
            semester = Applications.Semester.FIRST_SEMESTER,
            minimum_residency = 6,
            voters_validity_year_start = 2023,
            voters_validity_year_end = 2030,
        )

        self.stdout.write(self.style.SUCCESS("Successfully set constraints for eligibility checking."))
