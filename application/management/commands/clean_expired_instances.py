from django.core.management.base import BaseCommand
from django.utils import timezone
from application.models import Applications

class Command(BaseCommand):
    help = 'Delete instances with applicant_status="NEW APPLICANT" and is_eligibile=False older than 3 days'

    def handle(self, *args, **options):
        threshold_date = timezone.now - timezone.timedelta(days=3)

        # Filter instances with applicant_status="NEW APPLICANT" and is_eligible=False
        instances_to_delete = Applications.objects.filter(
            applicant_status='NEW APPLICANT',
            is_eligible=False,
            expires_at__lt=threshold_date  # Check expiration date
        )

        for instance in instances_to_delete:
            instance.delete()

        self.stdout.write(self.style.SUCCESS(f'Deleted {len(instances_to_delete)} instances'))