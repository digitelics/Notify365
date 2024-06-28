from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from settings.models import State
from django.urls import reverse
from django.utils import timezone
from settings.models import State
from security.models import CustomUser as User
from customers.models import Customer, CustomerService, Note, CustomerDocument, AdditionalContact
from collections import defaultdict
from django.http import JsonResponse
from django.db.models import F



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
def customer_detail_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user = customer.created_by
        state = customer.state
        deals = CustomerService.objects.filter(customer=customer_id).annotate(product_name=F('product__name')).values(
            'id', 'product_name', 'customer', 'code', 'activation_date', 'base_premium', 'created_by', 'activation_period', 'deactivation_date', 'product_status'
        ).order_by('-created_at')
        
        deal_list = list(deals)
        
        notes = Note.objects.filter(customer=customer_id).annotate(created_by_name=F('created_by__name')).values(
            'id', 'note', 'date', 'created_by_name', 'created_at'
        ).order_by('-date')
        
        note_list = list(notes)

        aditional_contact = AdditionalContact.objects.filter(customer=customer_id).annotate(contact_name=F('contact__first_name'), contact_last_name=F('contact__last_name'), contact_phone=F('contact__phone')).values('customer', 'contact_name', 'contact_last_name', 'contact_phone', 'relationship')
       
        documents = CustomerDocument.objects.filter(customer=customer_id).annotate(document_name=F('document__name'), created_by_name=F('created_by__name')).values('document_name', 'customer', 'doc_path', 'created_by_name', 'created_at')
       
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
            'contacts':list(aditional_contact)
        }
        return JsonResponse(data)
    else:
        user_subscription = request.user.suscription
        customers = Customer.objects.filter(deleted_at=None, created_by__suscription=user_subscription).order_by('first_name')
        customer_count = customers.count()
        grouped_customers = defaultdict(list)
        
        for customer_item in sorted(customers, key=lambda x: x.first_name):
            first_letter = customer_item.first_name[0].upper()
            grouped_customers[first_letter].append(customer_item)
        
        states = State.objects.all() 
    
        context = {
            'states':states,
            'grouped_customers': dict(grouped_customers),
            'customer_count': customer_count,
            'customer_created': customer,
        }
        return render(request, 'customers/customer_template.html', {'data':context})