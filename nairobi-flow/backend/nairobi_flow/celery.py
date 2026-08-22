import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nairobi_flow.settings")

app = Celery("nairobi_flow")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
