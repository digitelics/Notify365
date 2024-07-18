from django.db import models
from customers.models import Customer

class Notification(models.Model):
    EMAIL = 'email'
    TEXT = 'text'
    CALL = 'call'
    CHANNEL_CHOICES = [
        (EMAIL, 'Email'),
        (TEXT, 'Text'),
        (CALL, 'Call')
    ]

    template = models.ForeignKey('Template', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications')
    date = models.DateTimeField()
    channel = models.CharField(max_length=5, choices=CHANNEL_CHOICES)
    text = models.TextField()
    sent_by = models.TextField(default='Automatic notification')

    def __str__(self):
        notification_message = f'Notification: '

        if self.template:
            notification_message += f'{self.template.name} for '

        notification_message += f'{self.customer} on {self.date.strftime("%m-%d-%Y")} via {self.channel}'

        return notification_message