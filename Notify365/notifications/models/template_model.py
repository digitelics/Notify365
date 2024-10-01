from django.db import models
from simple_history.models import HistoricalRecords
from security.models import Suscription
from django.conf import settings

class Template(models.Model):
    BIRTHDAY = 'birthday'
    PENDING_DOCUMENT = 'pendingDocument'
    EXPIRY_TOMORROW = 'expiryTomorrow'
    PROMO = 'promo'
    NEXT_EXPIRY = 'nextExpiry'
    EXPIRY = 'expiry'
    PAYMENT_REMINDER = 'paymentReminder'
    SERVICE_EXPIRED = 'serviceExpired'
    SERVICE_PENDING_EXPIRED = 'servicePendingExpired'
    TYPE_CHOICES = [
        (BIRTHDAY, 'Birthday'), # Template para notificar a los clientes que cumplen años
        (PENDING_DOCUMENT, 'Pending Document'), # Template para notificar a los clientes que tengan documentos pendientes de enviar.
        (PROMO, 'Promo'), # Template para enviar promociones a los clientes
        (NEXT_EXPIRY, 'Next Expiry'), # Template para notificar a los clientes que su poliza expira en 7 dias
        (EXPIRY, 'Expiry'), # Template para notificar a los clientes que su poliza expiro hace 7 dias
        (PAYMENT_REMINDER, 'Payment Reminder'), # Template para notificar a los clientes que tienen pagos pendientes.
        (EXPIRY_TOMORROW, 'Expiry Tomorrow'), # Template para notificar a los clientes que su poliza expira el dia siguiente
        (SERVICE_EXPIRED, 'Service Expired'), # Template para notificar a los clientes que su poliza acaba de expirar.
        (SERVICE_PENDING_EXPIRED, 'Service Pending Expire'), # Template para notificar a los clientes que su poliza esta vencida pero se le daran unos dias de gracia antes de cancelarla
    ]
    
    ONCE = 'once'
    DAILY = 'Daily'
    EVERY3DAY = 'Every 3 days'
    WEEKLY = 'Weekly'
    BIWEEKLY = 'Biweekly'
    MONTHLY = 'Monthly'
    QUARTERLY = 'Quarterly'
    SEMIANUAL = 'Semi-annually'
    ANNUALLY = 'Annually'
    INTERVAL = [
        (ONCE, 'Once'),
        (DAILY, 'Daily'),
        (EVERY3DAY, 'Every 3 days'),
        (WEEKLY, 'Weekly'),
        (BIWEEKLY, 'Biweekly'),
        (MONTHLY, 'Monthly'),
        (QUARTERLY, 'Quarterly'),
        (SEMIANUAL, 'Semi-annually'),
        (ANNUALLY, 'Annually'),
    ]

    EMAIL = 'email'
    TEXT = 'text'
    CHANNEL_CHOICES = [
        (EMAIL, 'Email'),
        (TEXT, 'Text'),
    ]

    name = models.CharField(max_length=255)
    text = models.TextField()
    suscription = models.ForeignKey(Suscription, on_delete=models.CASCADE, related_name='templates')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    interval = models.CharField(max_length=30, choices=INTERVAL, default=ANNUALLY)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_templates'
    )
    channel_to = models.CharField(max_length=6, choices=CHANNEL_CHOICES, default="text")
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs.pop('user')
            self.suscription = user.suscription
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Template: {self.name} ({self.type}) for {self.suscription}'
