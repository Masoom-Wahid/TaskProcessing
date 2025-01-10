from __future__ import absolute_import, unicode_literals
import os
from celery import Celery



SETTINGS_MODULE = os.getenv("SETTINGS_MODULE") or "task_processor.settings"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_MODULE)

app = Celery('task_processor')

app.config_from_object('django.conf:settings', namespace='CELERY_')

app.autodiscover_tasks()


