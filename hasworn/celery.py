import os

from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_ready


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hasworn.settings')

app = Celery('hasworn')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'rebuild-wearer-sites-daily': {
        'task': 'hasworn.wearers.tasks.rebuild_all_wearer_sites',
        'schedule': crontab(hour=4, minute=1),
    },
}


@worker_ready.connect
def at_start(sender, **k):
    from django.conf import settings
    print(f'running with checkout {settings.COMMIT_SHA}')
