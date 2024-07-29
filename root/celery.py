from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

app = Celery('root')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.broker_url = 'redis://localhost:6379/0'

app.conf.enable_utc = False

app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
