from celery import shared_task
from django.utils import timezone
from customers.models import Customer, CustomerDocument, CustomerService
from notifications.models import Notification, Template
from django.conf import settings
from django.core.mail import send_mail
from security.models import CustomUser as User, Suscription
from utils import template_text
from django.db.models import Q, Exists, OuterRef
from datetime import timedelta
from utils.send_text_notification import send_sms
import logging


logger = logging.getLogger(__name__)

@shared_task
def send_birthday_notifications():
    today = timezone.now().date()
    current_month = today.month
    current_day = today.day
    
    suscriptions = Suscription.objects.all()
    total_notifications_sent = 0

    for suscription in suscriptions:
        customers = Customer.objects.filter(dob__month=current_month, dob__day=current_day, created_by__suscription=suscription.id)
        template = Template.objects.filter(type="birthday", created_by__suscription=suscription.id).first()
        if template:
            logger.info(f"No template found for subscription {suscription.id}")
            for customer in customers:
                text = template_text.getText(template.text, customer, False)
                Notification.objects.create(
                    template=template, 
                    text=text, 
                    customer=customer,
                    date=timezone.now(),
                    channel=template.channel_to,
                )
                send_sms(customer.phone, text)
                total_notifications_sent += 1
        else:
            logger.info(f"No template found for subscription {suscription.id}")


    return f'Sent birthday notifications to {total_notifications_sent} customers.'

@shared_task
def send_document_notifications():
    suscriptions = Suscription.objects.all()
    total_notifications_sent = 0

    for suscription in suscriptions:
        subquery = CustomerDocument.objects.filter(customer=OuterRef('pk'),created_by__isnull=True)
        customers = Customer.objects.filter(Exists(subquery)).distinct()
        template = Template.objects.filter(type="pendingDocument", created_by__suscription=suscription.id).first()
        if template:
            logger.info(f"No template found for subscription {suscription.id}")
            for customer in customers:
                text = template_text.getText(template.text, customer, True)
                Notification.objects.create(
                    template=template, 
                    text=text, 
                    customer=customer,
                    date=timezone.now(),
                    channel=template.channel_to,
                )
                send_sms(customer.phone, text)
                total_notifications_sent += 1
        else:
            logger.info(f"No template found for subscription {suscription.id}")


    return f'Sent pending document notifications to {total_notifications_sent} customers.'


@shared_task
def send_expiry_notifications():
    suscriptions = Suscription.objects.all()
    total_notifications_sent = 0
    today = timezone.now().date()

    for suscription in suscriptions:
        subquery = CustomerService.objects.filter( customer=OuterRef('pk'),deactivation_date__lt=today)
        customers = Customer.objects.filter(Exists(subquery)).distinct()
        template = Template.objects.filter(type="expiry", created_by__suscription=suscription.id).first()
        if template:
            logger.info(f"No template found for subscription {suscription.id}")
            for customer in customers:
                text = template_text.getText(template.text, customer, False)
                Notification.objects.create(
                    template=template, 
                    text=text, 
                    customer=customer,
                    date=timezone.now(),
                    channel=template.channel_to,
                )
                send_sms(customer.phone, text)
                total_notifications_sent += 1
        else:
            logger.info(f"No template found for subscription {suscription.id}")


    return f'Sent expiry notifications to {total_notifications_sent} customers.'


@shared_task
def send_next_expiry_notifications():
    suscriptions = Suscription.objects.all()
    total_notifications_sent = 0
    today = timezone.now().date()
    seven_days_from_now = today + timedelta(days=7)

    for suscription in suscriptions:
        subquery = CustomerService.objects.filter( customer=OuterRef('pk'),deactivation_date__gte=today, deactivation_date__lte=seven_days_from_now)
        customers = Customer.objects.filter(Exists(subquery)).distinct()
        template = Template.objects.filter(type="nextExpiry", created_by__suscription=suscription.id).first()
        if template:
            logger.info(f"No template found for subscription {suscription.id}")
            for customer in customers:
                text = template_text.getText(template.text, customer, False, True)
                Notification.objects.create(
                    template=template, 
                    text=text, 
                    customer=customer,
                    date=timezone.now(),
                    channel=template.channel_to,
                )
                send_sms(customer.phone, text)
                total_notifications_sent += 1
        else:
            logger.info(f"No template found for subscription {suscription.id}")


    return f'Sent next expiry notifications to {total_notifications_sent} customers.'


@shared_task
def send_expiry_tomorrow_notifications():
    suscriptions = Suscription.objects.all()
    total_notifications_sent = 0
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    for suscription in suscriptions:
        subquery = CustomerService.objects.filter( customer=OuterRef('pk'), deactivation_date=tomorrow)
        customers = Customer.objects.filter(Exists(subquery)).distinct()
        template = Template.objects.filter(type="expiryTomorrow", created_by__suscription=suscription.id).first()
        if template:
            logger.info(f"No template found for subscription {suscription.id}")
            for customer in customers:
                text = template_text.getText(template.text, customer, False, True)
                Notification.objects.create(
                    template=template, 
                    text=text, 
                    customer=customer,
                    date=timezone.now(),
                    channel=template.channel_to,
                )
                send_sms(customer.phone, text)
                total_notifications_sent += 1
        else:
            logger.info(f"No template found for subscription {suscription.id}")


    return f'Sent expiry tomorrow notifications to {total_notifications_sent} customers.'


@shared_task
def send_expired_service_notifications():
    suscriptions = Suscription.objects.all()
    total_notifications_sent = 0
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)

    for suscription in suscriptions:
        subquery = CustomerService.objects.filter(customer=OuterRef('pk'), deactivation_date=seven_days_ago)
        customers = Customer.objects.filter(Exists(subquery)).distinct()
        template = Template.objects.filter(type="serviceExpired", created_by__suscription=suscription.id).first()
        
        if template:
            for customer in customers:
                text = template_text.getText(template.text, customer, False, True)
                Notification.objects.create(
                    template=template, 
                    text=text, 
                    customer=customer,
                    date=timezone.now(),
                    channel=template.channel_to,
                )
                send_sms(customer.phone, text)
                total_notifications_sent += 1
        else:
            logger.info(f"No template found for subscription {suscription.id}")

    return f'Sent expired service notifications to {total_notifications_sent} customers.'
