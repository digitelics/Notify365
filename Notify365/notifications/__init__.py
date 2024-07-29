# notifications/__init__.py
from __future__ import absolute_import, unicode_literals

# Import Celery app
from Notify365.celery import app as celery_app

__all__ = ('celery_app',)