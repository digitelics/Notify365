from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from customers.models import Customer, CustomerService
from notifications.models import Notification
from datetime import timedelta
from django.db.models import Sum, Q, Count, F




# Create your views here.
from customers.views import client_view, customer_view, customer_service_view, note_view, document_view, contact_view, customer_send_text_message_view
from security.views import login_view, registration_view, user_view, account_view
from settings.views import setting_view, company_view, security_view, notification_view, general_view, product_view
from notifications.views import notify_view
from schedules.views import calendar_views
from webcall.views import call_view


from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    today = timezone.now().date()
    user = request.user
    suscription = user.suscription

    # Clientes creados hoy filtrados por suscripción
    new_customers_today = Customer.objects.filter(created_at__date=today, created_by__suscription=suscription)

    # Servicios creados hoy filtrados por suscripción
    new_services_today = CustomerService.objects.filter(created_at__date=today, created_by__suscription=suscription)

    # Clasificar servicios por tipo
    new_policies_today = new_services_today.filter(product_classification="new")
    renewals_today = new_services_today.filter(product_classification="renewal")
    endorsements_today = new_services_today.filter(product_classification="endorsement")

    # Calcular el total del base premium de los servicios creados hoy
    total_base_premium_today = new_services_today.aggregate(Sum('base_premium'))['base_premium__sum'] or 0

    # Clasificar clientes por estado
    leads = Customer.objects.filter(customer_status="lead", created_by__suscription=suscription)
    clients = Customer.objects.filter(customer_status='client', created_by__suscription=suscription)
    inactives_today = CustomerService.objects.filter(product_status='inactive', updated_at__date=today, created_by__suscription=suscription)

    customers_with_service_counts = Customer.objects.filter(created_by__suscription=suscription).annotate(
        total_services=Count('services'),
        inactive_services=Count('services', filter=Q(services__product_status='inactive'))
    )

    # Filtra los clientes que tienen el mismo número de servicios totales e inactivos
    customers_with_all_services_inactive = customers_with_service_counts.filter(
        total_services=F('inactive_services'),
        total_services__gt=0  # Asegúrate de que el cliente tenga al menos un servicio
    )

    customers_with_active_service = Customer.objects.filter(created_by__suscription=suscription).annotate(
        total_services=Count('services'),
        active_services=Count('services', filter=Q(services__product_status='active'))
    )

    # Filtra los clientes que tienen el mismo número de servicios totales e inactivos
    customers_with_services_active = customers_with_active_service.filter(
        total_services=F('active_services'),
        total_services__gt=0  # Asegúrate de que el cliente tenga al menos un servicio
    )

    last_24_hours = timezone.now() - timedelta(hours=24)
    unregistered_calls = Notification.objects.filter(channel='call',date__gte=last_24_hours).exclude(customer__isnull=False)

    context = {
        'new_customers_today': new_customers_today.count(),
        'new_policies_today': new_policies_today.count(),
        'renewals_today': renewals_today.count(),
        'endorsements_today': endorsements_today.count(),
        'total_base_premium_today': total_base_premium_today,
        'leads': leads.count(),
        'leads_list': leads,
        'calls':unregistered_calls,
        'clients': customers_with_services_active.count(),
        'clients_list': customers_with_services_active,
        'inactive_customers': customers_with_all_services_inactive.count(),
        'inacties_list': customers_with_all_services_inactive,
        'inactives_today': inactives_today.count(),
    }

    return render(request, 'index.html', context)

def test (request):
     return render(request, 'test.html', {})



    
     


