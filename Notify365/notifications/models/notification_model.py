from django.db import models
from customers.models import Customer
import os

class Notification(models.Model):
    EMAIL = 'email'
    TEXT = 'text'
    CALL = 'call'
    REPLY = 'reply'
    CHANNEL_CHOICES = [
        (EMAIL, 'Email'),
        (TEXT, 'Text'),
        (CALL, 'Call'),
        (REPLY, 'Reply'),
    ]

    template = models.ForeignKey('Template', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications')
    date = models.DateTimeField()
    channel = models.CharField(max_length=5, choices=CHANNEL_CHOICES)
    text = models.TextField()
    sent_by = models.TextField(default='Automatic notification')
    read = models.BooleanField(default=True)
    attach = models.FileField(upload_to='staticfiles/files/notification_attach/', blank=True, null=True)

    def __str__(self):
        notification_message = f'Notification: '

        if self.template:
            notification_message += f'{self.template.name} for '

        notification_message += f'{self.customer} on {self.date.strftime("%m-%d-%Y")} via {self.channel}'

        return notification_message
    
    def extension(self):
        name, extension = os.path.splitext(self.attach.name)
        return extension