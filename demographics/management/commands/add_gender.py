from django.core.management.base import BaseCommand

from demographics.models import Gender


class Command(BaseCommand):
    help = "Add Gender records to the database"

    def handle(self, *args, **options):
        # Your code to create Gender records goes here
        Gender.objects.create(gender_name="Male")
        Gender.objects.create(gender_name="Female")

        self.stdout.write(self.style.SUCCESS("Successfully added Gender records"))
