from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords
from security.models import Suscription
from settings.models import RequiredDocument

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True, max_length=255)
    documents = models.ManyToManyField(RequiredDocument, related_name='document')
    created_at = models.DateTimeField(auto_now_add=True)
    suscription = models.ForeignKey(Suscription, on_delete=models.CASCADE, related_name='suscription')
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_products')
    history = HistoricalRecords()

    def __str__(self):
        return self.name
