from django.db import models
from customers.models import Customer
from security.models import CustomUser as User

import os
from django.conf import settings

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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)
    date = models.DateTimeField()
    channel = models.CharField(max_length=5, choices=CHANNEL_CHOICES)
    text = models.TextField()
    sent_by = models.TextField(default='Automatic notification')
    read = models.BooleanField(default=True)
    read_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_notification', blank=True, null=True )
    attach = models.FileField(upload_to='static/files/notification_attach/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notification', blank=True, null=True )
    to_number = models.TextField(default='', blank=True, null=True)
    from_number = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        notification_message = f'Notification: '

        if self.template:
            notification_message += f'{self.template.name} for '

        notification_message += f'{self.customer} on {self.date.strftime("%m-%d-%Y")} via {self.channel}'

        return notification_message
    
    def extension(self):
        name, extension = os.path.splitext(self.attach.name)
        return extension