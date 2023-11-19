from django.core.management.base import BaseCommand
from django.utils import timezone
from application.models import Applications

class Command(BaseCommand):
    help = 'Delete instances with applicant_status="NEW APPLICANT"'