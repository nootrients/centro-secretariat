from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centro_secretariat.settings')

# create a Celery instance and configure it with your Django settings.
app = Celery('centro_secretariat')

# Load task modules from all registered Django app configs.
app.config_from_object(settings, namespace='CELERY')

# Celery Beat Settings

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

# Schedule the task to run every day at a specific time
app.conf.beat_schedule = {
    'clean-expired-instances': {
        'task': 'your_app.tasks.clean_expired_instances',
        'schedule': crontab(hour=18, minute=0),  # Adjust the time as needed, for context, it's set to run at 6pm
    },
}