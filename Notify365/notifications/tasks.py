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
        # Encontrar los clientes que tienen documentos pendientes
        subquery = CustomerDocument.objects.filter(customer=OuterRef('pk'), created_by__isnull=True)
        customers = Customer.objects.filter(Exists(subquery), created_by__suscription=suscription.id).distinct()

        # Obtener el template para "pendingDocument"
        template = Template.objects.filter(type="pendingDocument", created_by__suscription=suscription.id).first()
        if not template:
            logger.info(f"No template found for subscription {suscription.id}")
            continue

        for customer in customers:
            # Verificar si ya se ha enviado una notificación de este template a este cliente
            last_notification = Notification.objects.filter(template=template, customer=customer).order_by('-date').first()

            if last_notification:
                next_send_date = calculate_next_send_date(last_notification.date, template.interval)

                # Si el próximo envío es None (porque el intervalo es "Once") o la fecha actual es menor que el próximo envío, no enviamos.
                if next_send_date and timezone.now() < next_send_date:
                    logger.info(f"Skipping notification for customer {customer.id}. Next send date: {next_send_date}")
                    continue

            # Si no hay notificación previa o ya es tiempo de enviar otra notificación, la enviamos
            text = template_text.getText(template.text, customer, False)
            Notification.objects.create(
                template=template, 
                text=text, 
                customer=customer,
                date=timezone.now(),
                channel=template.channel_to,
            )
            # Simulación del envío del mensaje (puede ser un SMS o un correo electrónico)
            send_sms(customer.phone, text)

            total_notifications_sent += 1
            logger.info(f"Notification sent to customer {customer.id} for template {template.id}")

    return f'Sent pending document notifications to {total_notifications_sent} customers.'


@shared_task
def send_expiry_notifications():
    suscriptions = Suscription.objects.all()
    total_notifications_sent = 0
    today = timezone.now().date()

    for suscription in suscriptions:
        
        seven_days_ago = today - timedelta(days=7)

        renewed_services_subquery = CustomerService.objects.filter(
        customer=OuterRef('pk'),  # Mismo cliente
        product=OuterRef('product'),  # Mismo producto
        deactivation_date__gt=today,  # Fecha de desactivación mayor que hoy (renovación)
        deleted_at__isnull=True  # Excluir los eliminados
        )

        expired_services_subquery = CustomerService.objects.filter(
            customer=OuterRef('pk'),  # Relacionado con el mismo cliente
            deactivation_date__lt=seven_days_ago,  # Fecha de desactivación menor que hace 7 días
            deleted_at__isnull=True  # Asegurarte de no contar los eliminados
        ).exclude(
            Exists(renewed_services_subquery)  # Excluir si hay una renovación
        )

        customers = Customer.objects.filter(
            Exists(expired_services_subquery),  # Filtrar clientes con servicios expirados y sin renovación
            created_by__suscription=suscription.id  # Filtrar por suscripción del usuario actual (si aplica)
        ).distinct()  
              
        # Obtener el template para "expiry"
        template = Template.objects.filter(type="expiry", created_by__suscription=suscription.id).first()

        if not template:
            logger.info(f"No template found for subscription {suscription.id}")
            continue

        for customer in customers:

            if customer.do_not_disturb:
                continue
            
            # Verificar si ya se ha enviado una notificación de este template a este cliente
            last_notification = Notification.objects.filter(template=template, customer=customer).order_by('-date').first()

            if last_notification:
                next_send_date = calculate_next_send_date(last_notification.date, template.interval)

                # Si el próximo envío es None (porque el intervalo es "Once") o la fecha actual es menor que el próximo envío, no enviamos.
                if next_send_date and today < next_send_date.date():
                    logger.info(f"Skipping notification for customer {customer.id}. Next send date: {next_send_date}")
                    continue

            # Si no hay notificación previa o ya es tiempo de enviar otra notificación, la enviamos
            text = template_text.getText(template.text, customer, False, True) # Asume que tienes una función para personalizar el texto con datos del cliente
            Notification.objects.create(
                template=template, 
                text=text, 
                customer=customer,
                date=timezone.now(),
                channel=template.channel_to,
            )
            # Simulación del envío del mensaje (puede ser un SMS o correo electrónico)
            send_sms(customer.phone, text)

            total_notifications_sent += 1
            logger.info(f"Notification sent to customer {customer.id} for template {template.id}")

    return f'Sent expiry notifications to {total_notifications_sent} customers.'


@shared_task
def send_next_expiry_notifications():
    suscriptions = Suscription.objects.all()
    total_notifications_sent = 0
    today = timezone.now().date()
    seven_days_from_now = today + timedelta(days=7)

    for suscription in suscriptions:
        # Encontrar los clientes cuyos servicios expiran dentro de 7 días
        subquery = CustomerService.objects.filter(
            customer=OuterRef('pk'),
            deactivation_date__gte=today,
            deactivation_date__lte=seven_days_from_now
        )
        customers = Customer.objects.filter(
            Exists(subquery),
            created_by__suscription=suscription.id
        ).distinct()

        # Obtener el template para "nextExpiry"
        template = Template.objects.filter(type="nextExpiry", created_by__suscription=suscription.id).first()

        if not template:
            logger.info(f"No template found for subscription {suscription.id}")
            continue

        for customer in customers:
            # Verificar si ya se ha enviado una notificación de este template a este cliente
            last_notification = Notification.objects.filter(template=template, customer=customer).order_by('-date').first()

            if last_notification:
                next_send_date = calculate_next_send_date(last_notification.date, template.interval)

                # Si el próximo envío es None (porque el intervalo es "Once") o la fecha actual es menor que el próximo envío, no enviamos.
                if next_send_date and timezone.now().date() < next_send_date:
                    logger.info(f"Skipping notification for customer {customer.id}. Next send date: {next_send_date}")
                    continue

            # Si no hay notificación previa o ya es tiempo de enviar otra notificación, la enviamos
            text = template_text.getText(template.text, customer, False, True)
            Notification.objects.create(
                template=template, 
                text=text, 
                customer=customer,
                date=timezone.now(),
                channel=template.channel_to,
            )
            # Simulación del envío del mensaje (puede ser un SMS o un correo electrónico)
            send_sms(customer.phone, text)

            total_notifications_sent += 1
            logger.info(f"Notification sent to customer {customer.id} for template {template.id}")

    return f'Sent next expiry notifications to {total_notifications_sent} customers.'


@shared_task
def send_expiry_tomorrow_notifications():
    suscriptions = Suscription.objects.all()
    total_notifications_sent = 0
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    for suscription in suscriptions:
        # Encontrar los clientes cuyos servicios expiran mañana
        subquery = CustomerService.objects.filter(
            customer=OuterRef('pk'), 
            deactivation_date=tomorrow
        )
        customers = Customer.objects.filter(
            Exists(subquery),
            created_by__suscription=suscription.id
        ).distinct()

        # Obtener el template para "expiryTomorrow"
        template = Template.objects.filter(type="expiryTomorrow", created_by__suscription=suscription.id).first()

        if not template:
            logger.info(f"No template found for subscription {suscription.id}")
            continue

        for customer in customers:
            # Verificar si ya se ha enviado una notificación de este template a este cliente
            last_notification = Notification.objects.filter(template=template, customer=customer).order_by('-date').first()

            if last_notification:
                next_send_date = calculate_next_send_date(last_notification.date, template.interval)

                # Si el próximo envío es None (porque el intervalo es "Once") o la fecha actual es menor que el próximo envío, no enviamos.
                if next_send_date and timezone.now().date() < next_send_date:
                    logger.info(f"Skipping notification for customer {customer.id}. Next send date: {next_send_date}")
                    continue

            # Si no hay notificación previa o ya es tiempo de enviar otra notificación, la enviamos
            text = template_text.getText(template.text, customer, False, True)
            Notification.objects.create(
                template=template, 
                text=text, 
                customer=customer,
                date=timezone.now(),
                channel=template.channel_to,
            )
            # Simulación del envío del mensaje (puede ser un SMS o un correo electrónico)
            send_sms(customer.phone, text)

            total_notifications_sent += 1
            logger.info(f"Notification sent to customer {customer.id} for template {template.id}")

    return f'Sent expiry tomorrow notifications to {total_notifications_sent} customers.'



@shared_task
def send_expired_service_notifications():
    suscriptions = Suscription.objects.all()
    total_notifications_sent = 0
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)

    for suscription in suscriptions:
        # Encontrar los clientes cuyos servicios expiraron hace 7 días
        subquery = CustomerService.objects.filter(
            customer=OuterRef('pk'), 
            deactivation_date=seven_days_ago
        )
        customers = Customer.objects.filter(
            Exists(subquery),
            created_by__suscription=suscription.id
        ).distinct()

        # Obtener el template para "serviceExpired"
        template = Template.objects.filter(type="serviceExpired", created_by__suscription=suscription.id).first()

        if not template:
            logger.info(f"No template found for subscription {suscription.id}")
            continue

        for customer in customers:
            # Verificar si ya se ha enviado una notificación de este template a este cliente
            last_notification = Notification.objects.filter(template=template, customer=customer).order_by('-date').first()

            if last_notification:
                next_send_date = calculate_next_send_date(last_notification.date, template.interval)

                # Si el próximo envío es None (porque el intervalo es "Once") o la fecha actual es menor que el próximo envío, no enviamos.
                if next_send_date and timezone.now().date() < next_send_date:
                    logger.info(f"Skipping notification for customer {customer.id}. Next send date: {next_send_date}")
                    continue

            # Si no hay notificación previa o ya es tiempo de enviar otra notificación, la enviamos
            text = template_text.getText(template.text, customer, False, True)
            Notification.objects.create(
                template=template, 
                text=text, 
                customer=customer,
                date=timezone.now(),
                channel=template.channel_to,
            )
            # Simulación del envío del mensaje (puede ser un SMS o un correo electrónico)
            send_sms(customer.phone, text)

            total_notifications_sent += 1
            logger.info(f"Notification sent to customer {customer.id} for template {template.id}")

    return f'Sent expired service notifications to {total_notifications_sent} customers.'


# Función para calcular el próximo envío basado en el intervalo del template
def calculate_next_send_date(last_sent_date, interval):
    if interval == Template.ONCE:
        return None  # Solo se envía una vez
    elif interval == Template.DAILY:
        return last_sent_date + timedelta(days=1)
    elif interval == Template.EVERY3DAY:
        return last_sent_date + timedelta(days=3)
    elif interval == Template.WEEKLY:
        return last_sent_date + timedelta(weeks=1)
    elif interval == Template.BIWEEKLY:
        return last_sent_date + timedelta(weeks=2)
    elif interval == Template.MONTHLY:
        return last_sent_date + timedelta(weeks=4)  # Aproximadamente un mes
    elif interval == Template.QUARTERLY:
        return last_sent_date + timedelta(weeks=12)
    elif interval == Template.SEMIANUAL:
        return last_sent_date + timedelta(weeks=26)
    elif interval == Template.ANNUALLY:
        return last_sent_date + timedelta(weeks=52)
    return None