from django.shortcuts import render, redirect

from notifications.task import send_birthday_notifications, send_document_notifications, send_expiry_notifications, send_next_expiry_notifications, send_expiry_tomorrow_notifications
from django.contrib.auth.decorators import login_required


from customers.models import CustomerDocument, CustomerService
from datetime import timedelta
from django.utils import timezone

# Create your views here.

def notify(request):
    send_expiry_tomorrow_notifications.delay()
    send_birthday_notifications.delay()
    send_document_notifications.delay()
    send_expiry_notifications.delay()
    send_next_expiry_notifications.delay()
    return render(request, 'notifications/notify_template.html', {})

def sms(request):
    return render(request, 'notifications/text_message_template.html', {})



