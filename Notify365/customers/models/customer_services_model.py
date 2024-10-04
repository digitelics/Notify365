from django.db import models
from simple_history.models import HistoricalRecords
from customers.models import Customer # Ajusta la importación según tu estructura de carpetas
from settings.models import Product, Provider  # Ajusta la importación según tu estructura de carpetas
from security.models import CustomUser as User
from django.utils import timezone
from datetime import timedelta

class CustomerService(models.Model):
    SEMI_ANNUAL = 'semi-annual'
    ANNUAL = 'annual'
    UNDEFINED = 'undefined'
    ACTIVATION_PERIOD_CHOICES = [
        (SEMI_ANNUAL, 'Semi-Annual'),
        (ANNUAL, 'Annual'),
        (UNDEFINED, 'Undefined'),
    ]

    NEW = 'new'
    RENEWAL = 'renewal'
    ENDORSEMENT = 'endorsement'
    PRODUCT_CLASSIFICATION_CHOICES = [
        (NEW, 'New'),
        (RENEWAL, 'Renewal'),
        (ENDORSEMENT, 'Endorsement'),
    ]

    ACTIVE = 'active'
    INACTIVE = 'inactive'
    PRODUCT_STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='services')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='service')
    code = models.CharField(max_length=100)
    activation_date = models.DateField()
    base_premium = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='services_created')
    activation_period = models.CharField(max_length=20, choices=ACTIVATION_PERIOD_CHOICES)
    deactivation_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    product_classification = models.CharField(max_length=20, choices=PRODUCT_CLASSIFICATION_CHOICES)
    product_status = models.CharField(max_length=20, choices=PRODUCT_STATUS_CHOICES)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.customer} - {self.product}'

    def save(self, *args, **kwargs):
        
        if self.activation_period == self.SEMI_ANNUAL:
            self.deactivation_date = self.activation_date + timedelta(days=182)  # Aproximadamente 6 meses
        elif self.activation_period == self.ANNUAL:
            self.deactivation_date = self.activation_date + timedelta(days=365)  # Aproximadamente 1 año
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Customer Service'
        verbose_name_plural = 'Customer Services'
