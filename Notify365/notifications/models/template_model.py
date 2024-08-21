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
    TYPE_CHOICES = [
        (BIRTHDAY, 'Birthday'),
        (PENDING_DOCUMENT, 'Pending Document'),
        (PROMO, 'Promo'),
        (NEXT_EXPIRY, 'Next Expiry'),
        (EXPIRY, 'Expiry'),
        (PAYMENT_REMINDER, 'Payment Reminder'),
        (EXPIRY_TOMORROW, 'Expiry Tomorrow'),
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
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

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
