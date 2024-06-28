from django.shortcuts import render, redirect
from settings.models.company_model import Company, State
from security.models import Suscription, CustomUser as Users
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

# Create your views here.
@login_required
def company(request):
    user = request.user
    suscription = Suscription.objects.get(pk=user.suscription.id)
    company_id = user.suscription.company.id
    company = Company.objects.get(pk=company_id)
    logo_url = company.logo.url if company.logo else ''
    states = State.objects.all() 
    available_users = Users.objects.filter(suscription = suscription.id, deleted_at=None).count()
    current_date = timezone.now().date()
    status = current_date > suscription.expiration_date
    context = {
        'name':company.name,
        'address': company.address,
        'represented':company.representative,
        'logo':logo_url,
        'phone':company.phone,
        'created':company.created_at,
        'city':company.city,
        'zcode':company.zip_code,
        'state': company.state,
        'states':states,
        'expiration_date': suscription.expiration_date,
        'status': status,
        'activation_date': suscription.activation_date,
        'user_allowed': suscription.max_users,
        'montyhly_payment': suscription.cost,
        'available_users': suscription.max_users - available_users,

    }
    return render(request, "settings/company_template.html", {'data':context})

# Edit Company
@login_required
def edit_company(request):
    # Obtener la compañía del usuario logueado
    user = request.user
    company_id = user.suscription.company.id
    company_to_edit = Company.objects.get(pk=company_id)

    if request.method == 'POST':
        # Obtener los datos enviados por el formulario
        name = request.POST.get('company-name')
        address = request.POST.get('address')
        representative = request.POST.get('represented')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        state_id = request.POST.get('state')  # Se asume que el ID del estado es enviado
        zip_code = request.POST.get('zip-code')
        logo = request.FILES.get('logo')  # Handle file upload

        if not all([name, address, representative, phone, city, state_id, zip_code]):
            messages.add_message(request, messages.ERROR, 'All fields are required.', extra_tags='Updating_error error')
            return redirect('company')
        else:
            # Actualizar los datos de la compañía
            company_to_edit.name = name
            company_to_edit.address = address
            company_to_edit.representative = representative
            company_to_edit.phone = phone
            company_to_edit.city = city
            company_to_edit.state_id = state_id  # Asignar el ID del estado
            company_to_edit.zip_code = zip_code
            if logo:
                company_to_edit.logo = logo
            company_to_edit.save()

            messages.add_message(request, messages.SUCCESS, 'Company information updated successfully.', extra_tags='Company_updated success')
            return redirect('company')  # Cambia 'company' a la URL correcta

    # Si el método no es POST, renderiza el formulario con los datos actuales de la compañía
    
    messages.add_message(request, messages.ERROR, "Sorry, we can't complete this transaction.", extra_tags='Editing_error error')
    return redirect('company') 

