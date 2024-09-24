from django.db import models
from security.models import CustomUser as User
from customers.models import CustomerService  # Asegúrate de que el modelo Product esté definido en esta app
from django.utils import timezone

class PremiumTransaction(models.Model):
    # Definición de los valores para el campo 'type'
    PREMIUM_CANCEL = 'cancel'
    PREMIUM_WRITER = 'writer'
    
    TYPE_CHOICES = [
        (PREMIUM_CANCEL, 'Premium Cancel'),
        (PREMIUM_WRITER, 'Premium Writer'),
    ]

    # Relaciones
    deal = models.ForeignKey(CustomerService, on_delete=models.CASCADE, related_name='premium_transactions')
    
    # Campos
    premium = models.DecimalField(max_digits=10, decimal_places=2)  # Para almacenar cantidades de dinero con precisión
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)  # Para seleccionar entre 'Premium Cancel' o 'Premium Writer'
    date = models.DateTimeField(default=timezone.now)  # Fecha de creación del registro (se asigna la fecha actual)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='premium_transactions')

    def __str__(self):
        return f'Transaction for {self.deal} - {self.get_type_display()}'

    class Meta:
        verbose_name = 'Premium Transaction'
        verbose_name_plural = 'Premium Transactions'
