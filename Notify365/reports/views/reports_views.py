
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from customers.models import Customer, CustomerService, PremiumTransaction
from notifications.models import Notification
from datetime import timedelta, datetime
from django.db.models import Sum, Q, Count, F, FloatField, ExpressionWrapper, DateField
from django.utils import timezone
from settings.models import Provider, Product
from notifications.models import Notification
from security.models import CustomUser
from django.core.paginator import Paginator
from django.db.models.functions import TruncDate
import json
from collections import defaultdict

from django.utils.dateparse import parse_date







@login_required
def reports(request):
    return render(request, 'reports/reports_template.html', {})

@login_required
def list_client_by_company(request):
    user = request.user
    suscription = user.suscription
    provider_filter = request.POST.get('provider')  # Obtener el filtro del proveedor si se pasa

    # Filtrar por suscripción y aplicar anotaciones
    customers_with_active_service = Customer.objects.filter(
        created_by__suscription=suscription,
        services__product_status='active'
    ).annotate(
        total_services=Count('services'),
        active_services=Count('services', filter=Q(services__product_status='active'))
    )

    # Filtrar por proveedor si se ha pasado un proveedor en la solicitud
    if provider_filter:
        customers_with_active_service = customers_with_active_service.filter(services__provider__provider=provider_filter)

    # Obtener los datos de los servicios y proveedores relacionados
    customers_with_services = customers_with_active_service.prefetch_related('services__provider', 'services__product')

    paginator = Paginator(customers_with_services, 10)  # Paginar el queryset con 10 elementos por página
    page_number = request.GET.get('page')  # Obtener el número de página de la solicitud GET
    
    # Obtener la página solicitada o la primera página por defecto
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'customers': customers_with_services,
        }  # Pasar el objeto de página al contexto

   
    return render(request, 'reports/list_client_by_company_template.html', {'data':context})


@login_required
def remarketing(request):
    user = request.user
    suscription = user.suscription
    business_line = request.POST.get('bline')  # Obtener el filtro del proveedor si se pasa
    today = timezone.now().date()
    fifteen_days_from_now = today + timedelta(days=15)

    # Calculate the renewal date based on activation_date and activation_period
    semi_annual_days = 182  # approx 6 months
    annual_days = 365

    # Filter for clients with inactive or expired services
    expired_clients = Customer.objects.filter(
        Q(services__product_status='inactive') |
        Q(services__deactivation_date__lt=today),
        created_by__suscription=suscription
    )

    if business_line:
        expired_clients = expired_clients.filter(services__product__name=business_line)


    # Further filter clients whose renewal date is within the next 15 days
    renewal_clients = []
    for client in expired_clients:
        for service in client.services.all():
            renewal_date = None  # Ensure it has a value
            if service.activation_period == 'semi-annual':
                renewal_date = service.activation_date + timedelta(days=semi_annual_days)
            elif service.activation_period == 'annual':
                renewal_date = service.activation_date + timedelta(days=annual_days)
            
            renewal_date_no_year = renewal_date.replace(year=today.year)
            today_no_year = today.replace(year=today.year)
            # Check if renewal_date is set and within the next 15 days
            if renewal_date_no_year and today_no_year <= renewal_date_no_year <= fifteen_days_from_now:
                renewal_clients.append(client)
                break  # No need to check other services for the same client
    
    paginator = Paginator(renewal_clients, 10)  # Paginar el queryset con 10 elementos por página
    page_number = request.GET.get('page')  # Obtener el número de página de la solicitud GET
    
    # Obtener la página solicitada o la primera página por defecto
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'customers': renewal_clients,
    }
   
    return render(request, 'reports/remarketing_template.html', {'data':context})


@login_required
def total_client_by_company(request):
    today = timezone.now().date()  # Get the current date
    user = request.user
    suscription = user.suscription

    # Annotate each provider with total clients, active clients, and percentage of active clients
    providers_with_clients = Provider.objects.filter(
        suscription=suscription  # Ensure providers have services created by the current user's subscription
    ).annotate(
        total_clients=Count('customerservice__customer', distinct=True),  # Count total clients
        active_clients=Count(
            'customerservice__customer',
            filter=(
                (Q(customerservice__deactivation_date__isnull=True) | 
                 Q(customerservice__deactivation_date__gt=today)) &
                Q(customerservice__created_by__suscription=suscription)  # Ensure clients' services were created by the current user's subscription
            ),
            distinct=True
        ),
        # Calculate percentage of active clients
        active_percentage=ExpressionWrapper(
            (Count(
                'customerservice__customer',
                filter=(
                    (Q(customerservice__deactivation_date__isnull=True) | 
                     Q(customerservice__deactivation_date__gt=today)) &
                     Q(customerservice__created_by__suscription=suscription)  # Ensure clients' services were created by the current user's subscription
                ),
                distinct=True
            ) * 100) / Count('customerservice__customer', distinct=True),
            output_field=FloatField()
        )
    )

    # Prepare data for the chart
    labels = [provider.provider for provider in providers_with_clients] or ['No data'] # Provider names
    total_clients = [provider.total_clients for provider in providers_with_clients] or [0] # Total clients per provider
    active_clients = [provider.active_clients for provider in providers_with_clients] or [0] # Active clients per provider


    context = {
        'providers': providers_with_clients,
        'labels_json': json.dumps(labels),
        'total_clients_json': json.dumps(total_clients),
        'active_clients_json': json.dumps(active_clients),
    }

    return render(request, 'reports/total_client_by_company_template.html', {'data': context})


@login_required
def total_client_by_busines_line(request):
    user = request.user
    suscription = user.suscription
    today = timezone.now().date() 
    business_line = request.POST.get('bl') 
    
    provider_product_data = CustomerService.objects.filter(
            (Q(deactivation_date__isnull=True) | 
            Q(deactivation_date__gt=today)) &
            Q(product__suscription=suscription) &  # Filter for products with the matching subscription
            Q(created_by__suscription=suscription)  # Filter for customers created by a user with the matching subscription
        ).values('product__name') \
        .annotate(total_customers=Count('customer', distinct=True)) \
        .order_by('product__name')

    if business_line:
        provider_product_data = provider_product_data.filter(product__name=business_line)

    product_names = [entry['product__name'] for entry in provider_product_data]
    total_customers = [entry['total_customers'] for entry in provider_product_data]

    context = {
        'provider_product_data': provider_product_data,
        'product_names': product_names,
        'total_customers': total_customers
    }
    return render(request, 'reports/total_client_by_business_line_template.html', {'data': context})


@login_required
def inactive_client(request):
    user = request.user
    suscription = user.suscription
    provider_filter = request.POST.get('provider')  # Obtener el filtro del proveedor si se pasa

    # Filtrar por suscripción y aplicar anotaciones
    customers_with_inactive_service = Customer.objects.filter(
        created_by__suscription=suscription,
        customer_status='inactive'
    )

    # Filtrar por proveedor si se ha pasado un proveedor en la solicitud
    if provider_filter:
        customers_with_inactive_service = customers_with_inactive_service.filter(services__provider__provider=provider_filter, )

    # Obtener los datos de los servicios y proveedores relacionados
    customers_with_services = customers_with_inactive_service.prefetch_related('services__provider', 'services__product')

    paginator = Paginator(customers_with_services, 10)  # Paginar el queryset con 10 elementos por página
    page_number = request.GET.get('page')  # Obtener el número de página de la solicitud GET
    
    # Obtener la página solicitada o la primera página por defecto
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'customers': customers_with_services,
    }  # Pasar el objeto de página al contexto
   
    return render(request, 'reports/list_inactive_client_template.html', {'data': context})


@login_required
def agent_communications_view(request):
    user = request.user
    suscription = user.suscription

    # Obtener el rango de fechas desde el POST (o usar todo el periodo si no se especifica)
    start_date_str = request.POST.get('start_date', None)
    end_date_str = request.POST.get('end_date', None)

    # Si no se especifica una fecha de fin, usamos la fecha actual
    if not end_date_str:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Si no se especifica una fecha de inicio, usamos hoy
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date()

    # Ajustamos el rango de tiempo para incluir todo el día
    start_datetime = datetime.combine(start_date, datetime.min.time())  # Desde el inicio del día
    end_datetime = datetime.combine(end_date, datetime.max.time())      # Hasta el final del día

    # Filtramos las notificaciones que no son automáticas y están dentro del rango de fechas
    notifications = Notification.objects.filter(
        date__range=[start_datetime, end_datetime],
        channel='text',
    ).exclude(sent_by='Automatic notification')
   
    # Para cada notificación, buscaremos al usuario a partir del campo `sent_by` (coincidencia exacta en el campo `name` de `CustomUser`)
    valid_notifications = []
    for notification in notifications:
        try:
            # Buscamos al usuario en el modelo `CustomUser` por nombre completo (campo `name`)
            sender = CustomUser.objects.get(name=notification.sent_by, suscription=suscription)
        except CustomUser.DoesNotExist:
            # Si no encontramos al usuario, lo ignoramos
            continue

        # Si encontramos al usuario, incluimos esta notificación en las válidas
        valid_notifications.append(notification)
    
    # Agrupamos las notificaciones válidas por agente, cliente y día de comunicación
    communications_by_agent = Notification.objects.filter(
        id__in=[n.id for n in valid_notifications]  # Solo las notificaciones válidas
    ).annotate(
        communication_day=TruncDate('date')
    ).values(
        'created_by', 'customer', 'communication_day'
    ).distinct()  # Aseguramos que cada combinación de agente, cliente y día sea única
    
    # Diccionario para contar los clientes únicos por día y por agente
    agent_communications = defaultdict(int)
    customer_details_by_agent = defaultdict(list)

    # Iteramos las notificaciones y contamos los clientes únicos por agente y por día
    for communication in communications_by_agent:
        agent_id = communication['created_by']
        # Sumamos uno por cada combinación única de agente, cliente y día
        agent_communications[agent_id] += 1

        # Agregamos los detalles de los clientes contactados para cada agente
        customer = Customer.objects.get(id=communication['customer'])
        customer_details_by_agent[agent_id].append({
            'id':customer.id,
            'name': f"{customer.first_name} {customer.last_name}",
            'phone': customer.phone,  # Asegúrate de que el campo 'phone' exista en el modelo Customer
            'communication_day': communication['communication_day']
        })

    for agent_id, customers in customer_details_by_agent.items():
        customers.sort(key=lambda x: x['communication_day'], reverse=True)

    # Obtener la lista de agentes involucrados
    agents_with_communications = CustomUser.objects.filter(
        id__in=communications_by_agent.values('created_by')
    ).order_by('name')
    
    # Creamos una lista que incluya los agentes con su número de comunicaciones y detalles de clientes
    agents_with_communications_data = []
    for agent in agents_with_communications:
        agents_with_communications_data.append({
            'id': agent.id,
            'name': agent.name,
            'total_communications': agent_communications.get(agent.id, 0),  # Acceder al diccionario para obtener el conteo
            'customers': customer_details_by_agent.get(agent.id, [])  # Detalles de los clientes contactados
        })
    # Pasamos los datos al contexto
    context = {
        'agents_with_communications_data': agents_with_communications_data,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'reports/responded_messages_by_agent.html', {'data': context})


@login_required
def agent_answered_calls_view(request):
    # Obtiene el usuario logueado
    current_user = request.user

    # Filtra todos los agentes cuya suscripción sea igual a la del usuario logueado
    agents = CustomUser.objects.filter(suscription=current_user.suscription)

    # Filtros de fecha opcionales
    start_date_str = request.POST.get('start_date')
    end_date_str = request.POST.get('end_date')


     # Si no se especifica una fecha de fin, usamos la fecha actual
    if not end_date_str:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Si no se especifica una fecha de inicio, usamos hoy
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date()

    # Ajustamos el rango de tiempo para incluir todo el día
    start_datetime = datetime.combine(start_date, datetime.min.time())  # Desde el inicio del día
    end_datetime = datetime.combine(end_date, datetime.max.time())   

    # Filtra las notificaciones (llamadas) realizadas o contestadas por los agentes en el rango de fecha
    calls_by_agent = Notification.objects.filter(
        created_by__in=agents,
        channel='call',
        date__range=[start_datetime, end_datetime]
    ).values('created_by__name').annotate(call_count=Count('id')).order_by('-call_count')

    # Pasar los agentes y la cantidad de llamadas al contexto
    context = {
        'calls_by_agent': calls_by_agent,  # Lista de diccionarios con agente y conteo de llamadas
    }

    return render(request, 'reports/answered_calls_by_agent.html', {'data': context})


@login_required
def premium_balance(request):
    user = request.user
    suscription = user.suscription
    
    # Obtener los filtros de la solicitud POST
    provider_filter = request.POST.get('provider')
    start_date_str = request.POST.get('start_date')
    end_date_str = request.POST.get('end_date')
    customer_filter = request.POST.get('customer')
    code_filter = request.POST.get('code')
    
    # Parsear las fechas si se proporcionan
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    # Filtrar las transacciones por la suscripción del usuario
    transactions = PremiumTransaction.objects.filter(
        created_by__suscription=suscription
    ).order_by('-date')

    # Aplicar los filtros adicionales si se proporcionan
    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])
    elif start_date:
        transactions = transactions.filter(date__gte=start_date)
    elif end_date:
        transactions = transactions.filter(date__lte=end_date)

    if customer_filter:
        customer_names = customer_filter.split()
        if len(customer_names) == 1:
            transactions = transactions.filter(
                Q(deal__customer__first_name__icontains=customer_names[0]) |
                Q(deal__customer__last_name__icontains=customer_names[0])
            )
        elif len(customer_names) >= 2:
            first_name = customer_names[0]
            last_name = ' '.join(customer_names[1:])
            transactions = transactions.filter(
                Q(deal__customer__first_name__icontains=first_name) &
                Q(deal__customer__last_name__icontains=last_name)
            )
    
    if code_filter:
        transactions = transactions.filter(deal__code__icontains=code_filter)

    # Calcular la sumatoria de premium por tipo
    write_sum = transactions.filter(type='writer').aggregate(Sum('premium'))['premium__sum'] or 0
    cancel_sum = transactions.filter(type='cancel').aggregate(Sum('premium'))['premium__sum'] or 0

    # Calcular el porcentaje y valores ajustados
    net_write = write_sum - cancel_sum
    cancel_percentage = (cancel_sum / write_sum) * 100 if write_sum != 0 else 0
    write_percentage = 100 - cancel_percentage

    # Paginación
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Contexto para el template
    context = {
        'page_obj': page_obj,
        'provider_filter': provider_filter,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'customer_filter': customer_filter,
        'code_filter': code_filter,
        'write_sum': write_sum,
        'cancel_sum': cancel_sum,
        'net_write': net_write,
        'write_percentage': write_percentage,
        'cancel_percentage': cancel_percentage,
    }

    return render(request, 'reports/premium_balance_template.html', {'data': context})
