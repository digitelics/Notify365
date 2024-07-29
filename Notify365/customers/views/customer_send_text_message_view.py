from utils import send_text_notification
from django.contrib.auth.decorators import login_required
from customers.models import Customer
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from notifications.models import Notification


@login_required
def customer_send_message(request):
    if request.method == 'POST':
        customerId = request.POST.get('customerId')
        message = request.POST.get('message')
        to = request.POST.get('to')

        if customerId and message and to:
            customer = Customer.objects.get(pk=customerId)
            status = send_text_notification.send_sms(to, message)
            if status:
                notification = Notification(
                    customer = customer,
                    channel = Notification.TEXT,
                    date = timezone.now(),
                    sent_by = request.user,
                    text = message,
                )
                notification.save()
                messages.add_message(request, messages.SUCCESS, 'Message sent successfully.', extra_tags='Message_sent success')
                return redirect(reverse('customer_detail', args=[customerId] ))
            else:
                messages.add_message(request, messages.ERROR, 'Something went wrong. Please contact the system administrator.', extra_tags='Sending_error error')
                return redirect(reverse('customer_detail', args=[customerId] ))
        else:
            messages.add_message(request, messages.ERROR, 'Error sending message. Please provide all required fields.', extra_tags='Sending_error error')
            return redirect(reverse('customers'))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Sending_error error')
    return redirect(reverse('customers'))