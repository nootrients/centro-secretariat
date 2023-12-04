from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Applications, AuditLog

@receiver(post_save, sender=Applications)
def log_application_action(sender, instance, created, **kwargs):
    if not created:
        # The application instance already exists, so it's an update
        if instance.application_status == 'ACCEPTED':
            action_type = 'ACCEPTED'
        elif instance.application_status == 'REJECTED':
            action_type = 'REJECTED'
        else:
            # If neither accepted nor rejected, it's some other update; skip logging
            return

        AuditLog.objects.create(
            action_type = action_type,
            application_id = instance,
            officer = instance.evaluated_by,
        )