from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from settings.models import State
from django.urls import reverse
from django.utils import timezone
from settings.models import State, Product, Provider, RequiredDocument
from security.models import CustomUser as User
from customers.models import Customer, CustomerService, Note, CustomerDocument, AdditionalContact, PremiumTransaction
from notifications.models import Notification, Template
from collections import defaultdict
from django.http import JsonResponse
from django.db.models import F
from django.conf import settings
import pandas as pd
from django.db import transaction
from utils.send_text_notification import send_sms
from utils import template_text





from dotenv import load_dotenv
load_dotenv()

@login_required
def customer(request):
    user_subscription = request.user.suscription
    customers = Customer.objects.filter(deleted_at=None, created_by__suscription=user_subscription).order_by('first_name')
    customer_count = customers.count()
    grouped_customers = defaultdict(list)

    for customer in sorted(customers, key=lambda x: x.first_name):
        first_letter = customer.first_name[0].upper()
        grouped_customers[first_letter].append(customer)
    
    states = State.objects.all()

    context = {
        'states':states,
        'grouped_customers': dict(grouped_customers),
        'customer_count': customer_count
    }
    return render(request, 'customers/customer_template.html', {'data':context})



@login_required
def add_customer_view(request):
    redirect_tab = 'customer'
    if request.method == 'POST':
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state_id = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        dob = request.POST.get('dob') or None
        gender = request.POST.get('gender')

        # Fetching state
        state = get_object_or_404(State, pk=state_id)

        if first_name and last_name and phone:
            if not phone.startswith('+1'):
                phone = '+1' + phone.lstrip('0')
            # Creating the customer
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                street=street,
                city=city,
                state=state,
                zip_code=zip_code,
                dob=dob,
                gender= gender,
                created_by=request.user,
                created_at=timezone.now(),
            )

            messages.add_message(request, messages.SUCCESS, 'Customer added successfully.', extra_tags='customer_added success')
            return redirect(reverse('customer_detail', args=[customer.id] ))
        else:
            messages.add_message(request, messages.ERROR, 'Error creating customer. Please provide all required fields.', extra_tags='Adding_error error')
            return redirect(reverse('customers'))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Adding_error error')
    return redirect(reverse('customers'))

@login_required
def edit_customer_view(request, id):
    redirect_tab = 'customer'
    if request.method == 'POST':
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state_id = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        dob = request.POST.get('dob') or None
        gender = request.POST.get('gender')

        # Fetching state
        state = State.objects.get(pk=state_id)
        print(state)
        customer = Customer.objects.get(pk=id)
        
        if not phone.startswith('+1'):
            phone = '+1' + phone.lstrip('0')
        # Creating the customer
        
        customer.first_name=first_name
        customer.last_name=last_name
        customer.phone=phone
        customer.email=email
        customer.street=street
        customer.city=city
        customer.state=state
        customer.zip_code=zip_code
        customer.dob=dob
        customer.gender= gender
        customer.save()

        messages.add_message(request, messages.SUCCESS, 'Customer updated successfully.', extra_tags='customer_updated success')
        return redirect(reverse('customer_detail', args=[customer.id] ))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Adding_error error')
    return redirect(reverse('customers'))


@login_required
def delete_customer(request, id):
    # Obtener el usuario que se va a editar
    customer_to_delete = Customer.objects.get(pk=id)

    if request.method == 'POST':
        
        # Actualizar los datos del usuario
        customer_to_delete.deleted_at = timezone.now()
        customer_to_delete.save()

        messages.add_message(request, messages.SUCCESS, 'Customer delete successfully.', extra_tags='Delete_customer success')
        return redirect('customers')
    
    messages.add_message(request, messages.WARNING, "We can't find that Customer.", extra_tags='Alert! warning')
    return redirect('customers')

@login_required
def customer_detail_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user = customer.created_by
        state = customer.state
        deals = CustomerService.objects.filter(customer=customer_id).annotate(product_name=F('product__name'), provider_name=F('provider__provider')).values(
            'id', 'product_name', 'customer', 'code', 'activation_date', 'base_premium', 'created_by', 'activation_period', 'deactivation_date', 'product_status', 'provider_name'
        ).order_by('-created_at')
        
        deal_list = list(deals)
        
        notes = Note.objects.filter(customer=customer_id).annotate(created_by_name=F('created_by__name')).values(
            'id', 'note', 'date', 'created_by_name', 'created_at'
        ).order_by('-date')
        
        note_list = list(notes)

        aditional_contact = AdditionalContact.objects.filter(customer=customer_id).annotate(contact_name=F('contact__first_name'), contact_last_name=F('contact__last_name'), contact_phone=F('contact__phone')).values('contact', 'customer', 'contact_name', 'contact_last_name', 'contact_phone', 'relationship')
       
        documents = CustomerDocument.objects.filter(customer=customer_id).annotate(document_name=F('document__name'), created_by_name=F('created_by__name')).values('id','document_name', 'customer', 'doc_path', 'created_by_name', 'created_at', 'updated_at')
       
        all_document = RequiredDocument.objects.filter(suscription=request.user.suscription, deleted_at=None).values('name', 'id')

        notifications = Notification.objects.filter(customer=customer_id).values('customer', 'date', 'channel', 'text', 'sent_by', 'attach').order_by('-date')
        for notification in notifications:
            notification['date'] = notification['date'].strftime('%b %d, %Y %I:%M%p').lower().replace('am', 'am').replace('pm', 'pm')

        services = Product.objects.filter(suscription=request.user.suscription, deleted_at=None).values('name', 'id')
        providers = Provider.objects.filter(suscription=request.user.suscription, deleted_at=None).values('provider', 'id')    
        data = {
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'phone': customer.phone,
            'email': customer.email if customer.email else '-',
            'street': customer.street,
            'city': customer.city,
            'zip_code': customer.zip_code,
            'dob': customer.dob.strftime('%m-%d-%Y') if customer.dob else '-',
            'customer_status': customer.get_customer_status_display(),
            'gender': customer.get_gender_display(),
            'created_by': user.name,
            'last_change': customer.updated_at.strftime('%m-%d-%Y'),
            'state': state.abbreviation,
            'deals': deal_list,
            'notes': note_list,
            'documents': list(documents),
            'contacts':list(aditional_contact),
            'notifications':list(notifications),
            'services':list(services),
            'providers':list(providers),
            'base_url': settings.BASE_URL,
            'all_document': list(all_document)
        }
        return JsonResponse(data)
    else:
        user_subscription = request.user.suscription
        customers = Customer.objects.filter(deleted_at=None, created_by__suscription=user_subscription).order_by('first_name')
        customer_count = customers.count()
        grouped_customers = defaultdict(list)
        aditional_contact = AdditionalContact.objects.filter(customer=customer_id).annotate(contact_name=F('contact__first_name'), contact_last_name=F('contact__last_name'), contact_phone=F('contact__phone')).values('contact', 'customer', 'contact_name', 'contact_last_name', 'contact_phone', 'relationship')


        services = Product.objects.filter(suscription=request.user.suscription, deleted_at=None).values('name', 'id')
        providers = Provider.objects.filter(suscription=request.user.suscription, deleted_at=None).values('provider', 'id') 
        all_document = RequiredDocument.objects.filter(suscription=request.user.suscription, deleted_at=None).values('name', 'id')

        deals = CustomerService.objects.filter(customer=customer_id).annotate(product_name=F('product__name'), provider_name=F('provider__provider')).values(
            'id', 'product_name', 'customer', 'code', 'activation_date', 'base_premium', 'created_by', 'activation_period', 'deactivation_date', 'product_status', 'provider_name'
        ).order_by('-created_at')

        notes = Note.objects.filter(customer=customer_id).annotate(created_by_name=F('created_by__name')).values(
            'id', 'note', 'date', 'created_by_name', 'created_at'
        ).order_by('-date')

        documents = CustomerDocument.objects.filter(customer=customer_id).annotate(document_name=F('document__name'), created_by_name=F('created_by__name')).values('id', 'document_name', 'customer', 'doc_path', 'created_by_name', 'created_at', 'updated_at')

        for customer_item in sorted(customers, key=lambda x: x.first_name):
            first_letter = customer_item.first_name[0].upper()
            grouped_customers[first_letter].append(customer_item)
        
        states = State.objects.all() 

        notifications = Notification.objects.filter(customer=customer_id).values('customer', 'date', 'channel', 'text', 'sent_by', 'attach').order_by('-date')
        for notification in notifications:
            notification['date'] = notification['date'].strftime('%b %d, %Y %I:%M%p').lower().replace('am', 'am').replace('pm', 'pm')

    
        context = {
            'states':states,
            'grouped_customers': dict(grouped_customers),
            'customer_count': customer_count,
            'customer_created': customer,
            'deals':deals,
            'notes':notes,
            'documents': documents,
            'services':list(services),
            'providers':list(providers),
            'base_url': settings.BASE_URL,
            'contacts' : aditional_contact,
            'customer_id':customer_id,
            'notifications':list(notifications),
            'all_document': list(all_document)
        }
        return render(request, 'customers/customer_template.html', {'data':context})
    
@login_required
def filter_customer_view(request):
    first_name = request.POST.get('first-name') or None
    last_name = request.POST.get('last-name') or None
    phone = request.POST.get('phone') or None
    email = request.POST.get('email') or None
    dob = request.POST.get('dob') or None
    policy = request.POST.get('policy-number') or None
    status = request.POST.get('customer-status-filter') or None

    user_subscription = request.user.suscription
    customers = Customer.objects.filter(created_by__suscription=user_subscription)

    # Aplicar filtros según los parámetros recibidos
    if first_name:
        customers = customers.filter(first_name__icontains=first_name)
    if last_name:
        customers = customers.filter(last_name__icontains=last_name)
    if phone:
        customers = customers.filter(phone__icontains=phone)
    if email:
        customers = customers.filter(email__icontains=email)
    if dob:
        customers = customers.filter(dob=dob)
    if policy:
        customers = customers.filter(services__code__icontains=policy)
    if status:
        customers = customers.filter(customer_status=status)
    else:
        customers = Customer.objects.filter(deleted_at=None, created_by__suscription=user_subscription)

    customers = customers.order_by('first_name')
    customer_count = customers.count()
    grouped_customers = defaultdict(list)

    for customer in customers:
        first_letter = customer.first_name[0].upper()
        grouped_customers[first_letter].append(customer)
    
    states = State.objects.all()

    context = {
        'states': states,
        'grouped_customers': dict(grouped_customers),
        'customer_count': customer_count
    }
    return render(request, 'customers/customer_template.html', {'data': context})

# ESTE METODO SE ACTIVA 
@login_required
def cancel_customers_automatically(request):
    if request.method == 'POST':
            excel_file = request.FILES.get('customer-list-file')
            count = 0
            if excel_file:
                try:
                    # Read the Excel file using pandas
                    df = pd.read_excel(excel_file)

                    with transaction.atomic():
                        for _, row in df.iterrows():
                            # Save data
                            poliza=row['PolicyNumber']
                            status = row['CSRStatus']
                            cancel_base_premium =row['CancelBasePremium']
                            if status == 'Canceled' or status == 'Canceled in Follow Up':
                                try:
                                    customerService = CustomerService.objects.get(code=poliza)
                                    customerService.product_status = 'inactive'
                                    customerService.deactivation_date = timezone.now()
                                    customerService.save()

                                    premium_transaction = PremiumTransaction(
                                        deal = customerService,
                                        premium = cancel_base_premium,
                                        type = 'cancel',
                                        created_by = request.user
                                    )
                                    premium_transaction.save()

                                    template = Template.objects.filter(type="serviceExpired", suscription=request.user.suscription).first()
                                    if template:
                                        customer = Customer.objects.get(pk=customerService.customer.id)
                                        text = template_text.getText(template.text, customer, False, True)
                                        
                                        send_sms(customer.phone, text)
                                        notification = Notification(
                                            template = template,
                                            customer = customer, 
                                            date = timezone.now(),
                                            channel = template.channel_to,
                                            text = template.text,
                                            sent_by = request.user,
                                            to_number = customer.phone,
                                            created_by = request.user,
                                        )
                                        notification.save()
                                    count = count =+ 1
                                except:
                                    pass
                            elif status == 'Not Called':
                                if True:
                                    customerService = CustomerService.objects.get(code=poliza)
                                    template = Template.objects.filter(type="servicePendingExpired", suscription=request.user.suscription).first()
                                    if template:
                                        customer = Customer.objects.get(pk=customerService.customer.id)
                                        text = template_text.getText(template.text, customer, False, True)
                                        send_sms(customer.phone, text)
                                        notification = Notification(
                                            template = template,
                                            customer = customer, 
                                            date = timezone.now(),
                                            channel = template.channel_to,
                                            text = template.text,
                                            sent_by = request.user,
                                            to_number = customer.phone,
                                            created_by = request.user,
                                        )
                                        notification.save()
                                    count = count =+ 1
                                else:
                                    pass

                            
                        messages.add_message(request, messages.SUCCESS, 'Initial data imported successfully. We add ' + str(count) + ' new customers', extra_tags='File_imported success')
                        return redirect(reverse('customers'))
                except:
                    messages.add_message(request, messages.ERROR, 'Error importing data. Please provide all required fields.', extra_tags='Importing_error error')
                    return redirect(reverse('customers'))     
            else:
                messages.add_message(request, messages.ERROR, 'Error importing data. Please provide all required fields.', extra_tags='Importing_error error')
                return redirect(reverse('customers'))
    
    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Importing_error error')
    return redirect(reverse('customers'))