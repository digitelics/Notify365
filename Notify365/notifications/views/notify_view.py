from django.shortcuts import render, redirect
from customers.models import Customer
from notifications.task import send_birthday_notifications, send_document_notifications, send_expiry_notifications, send_next_expiry_notifications, send_expiry_tomorrow_notifications
from django.contrib.auth.decorators import login_required
from notifications.models import Notification
from django.utils import timezone
from utils import send_text_notification
from django.contrib import messages
from django.urls import reverse
from django.conf import settings


# Create your views here.

def notify(request):
    send_expiry_tomorrow_notifications.delay()
    send_birthday_notifications.delay()
    send_document_notifications.delay()
    send_expiry_notifications.delay()
    send_next_expiry_notifications.delay()
    return render(request, 'notifications/notify_template.html', {})

@login_required
def sms(request, customer_id=None):
    customers = Customer.objects.filter(notifications__channel__in=['text', 'reply']).distinct()
    selected_customer = None

    for customer in customers:
        customer.notifications_list = customer.notifications.filter(channel__in=['text', 'reply']).order_by('-date')
        if customer_id and customer.id == int(customer_id):
            selected_customer = customer

    context = {
        'customers': customers,
        'selected_customer_id': selected_customer.id if selected_customer else None
    }

    return render(request, 'notifications/text_message_template.html', context)


@login_required
def send_message_chat(request):
    if request.method == 'POST':
        customerId = request.POST.get('customer-id')
        message = request.POST.get('message-text')
        attach = request.FILES.get('document-file')
        if customerId and message:
            customer = Customer.objects.get(pk=customerId)
            if attach:
                url = settings.BASE_URL +  "static/files/notification_attach/" + attach.name
                status = send_text_notification.send_sms(customer.phone, message, url)
            else:
                status = send_text_notification.send_sms(customer.phone, message)
            if status:
                notification = Notification(
                    customer = customer,
                    channel = Notification.TEXT,
                    date = timezone.now(),
                    sent_by = request.user,
                    text = message,
                    attach = attach
                )
                notification.save()
                messages.add_message(request, messages.SUCCESS, 'Message sent successfully.', extra_tags='Message_sent success')
                return redirect(reverse('sms_detail', args=[customerId] ))
            else:
                messages.add_message(request, messages.ERROR, 'Something went wrong. Please contact the system administrator.', extra_tags='Sending_error error')
                return redirect(reverse('sms_detail', args=[customerId] ))
        else:
            messages.add_message(request, messages.ERROR, 'Error sending message. Please provide all required fields.', extra_tags='Sending_error error')
            return redirect(reverse('sms'))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Sending_error error')
    return redirect(reverse('sms'))




