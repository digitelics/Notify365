from django.db import models
from simple_history.models import HistoricalRecords
from .state_model import State


class Company(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    representative = models.CharField(max_length=100)
    phone = models.CharField(max_length=15) # Este es el numero de telefono desde donde recibira llamadas.
    zip_code = models.CharField(max_length=10, null=True, blank=True)  
    city = models.CharField(max_length=100,  null=True, blank=True)     
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(upload_to='static/images/logos/', null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name