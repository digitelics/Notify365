# myproject/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notify365.settings')

app = Celery('Notify365')

# Usar una cadena de configuración para no necesitar el objeto de configuración adicional
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar automáticamente los módulos de tareas de todas las aplicaciones registradas en Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

