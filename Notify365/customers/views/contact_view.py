from django.contrib.auth.decorators import login_required
from security.models import CustomUser as User
from customers.models import Customer, AdditionalContact
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db import transaction

@login_required
def add_contact_view(request):
    redirect_tab = 'customer'
    if request.method == 'POST':
        customerId = request.POST.get('customerId')
        name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        relationship = request.POST.get('relationship')
        gender = request.POST.get('gender')
        contact_street = request.POST.get('contact-street')
        contact_city = request.POST.get('contact-city')
        contact_zcode = request.POST.get('contact-zip-code')
        print(customerId)
        try:
            with transaction.atomic():
                if customerId:
                    customer = Customer.objects.get(pk=customerId)
                    contact = Customer(
                        first_name=name,
                        last_name=last_name,
                        phone=phone,
                        street=contact_street if contact_street else customer.street,
                        city=contact_city if contact_city else customer.city,
                        state_id=customer.state.id ,
                        zip_code=contact_zcode if contact_zcode else customer.zip_code,
                        dob=dob,
                        gender=gender,
                        created_by=request.user,
                    )
                    contact.save()

                    additional_contact = AdditionalContact(
                        customer=customer,
                        contact=contact,
                        relationship=relationship,
                        created_by=request.user,
                    )
                    additional_contact.save()

                    messages.add_message(request, messages.SUCCESS, 'Contact added successfully.', extra_tags='Contact_added success')
                    return redirect(reverse('customer_detail', args=[customerId]))
                else:
                    messages.add_message(request, messages.ERROR, 'Error creating additional contact. Please provide all required fields.', extra_tags='Contact_error error')
                    return redirect(reverse('customers'))

        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Error creating contact: {e}', extra_tags='Adding_error error')
            return redirect(reverse('customers'))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Adding_error error')
    return redirect(reverse('customers'))
