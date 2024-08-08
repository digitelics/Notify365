from django.db import models
from settings.models.company_model import Company
from django.conf import settings
from simple_history.models import HistoricalRecords


class Suscription(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='suscription')
    is_active = models.BooleanField(default=True)
    activation_date = models.DateField()
    expiration_date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_suscriptions')
    max_users = models.PositiveIntegerField(default=1) 
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    history = HistoricalRecords()

    def __str__(self):
        return f"Suscription for {self.company}"
