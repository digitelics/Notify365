from django.shortcuts import render, redirect, get_object_or_404
from settings.models.company_model import Company, State
from security.models import Suscription, CustomUser as Users
from customers.models import Customer, CustomerService
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
import pandas as pd
from django.db import transaction
from datetime import datetime




# Create your views here.
@login_required
def data_import(request):
    return render(request, "settings/import_template.html", {})

def file_import(request):
        if request.method == 'POST':
            excel_file = request.FILES.get('document-file')
            count = 0
            if excel_file:
                try:
                    # Read the Excel file using pandas
                    df = pd.read_excel(excel_file)

                    with transaction.atomic():
                        for _, row in df.iterrows():
                            # Save data to the Provider model
                            poliza=row['PolicyNumberQQ']
                            first_name, last_name = split_name(row['ClientName'])
                            phone=str(row['CellPhone'])
                            email=row['email']
                            status=row['PolicyStatus']
                            company=row['company']
                            expiration=row['PolicyExpirationDateTime']
                            
                            state = get_object_or_404(State, abbreviation='FL')

                            if not phone.startswith('+1'):
                                phone = '+1' + phone.lstrip('0')

                            if status == "A":  
                                  customer_status = 'client'
                            elif status == "P":
                                 customer_status = 'lead'
                            else:
                                 customer_status = 'inactive'

                            customer, created = Customer.objects.get_or_create(
                                first_name=first_name,
                                last_name=last_name,
                                phone=phone,
                                email=email,
                                dob=timezone.now(),
                                state=state,
                                defaults={
                                    'created_by': request.user,
                                    'customer_status': customer_status,
                                    'created_at': timezone.now(),
                                    'deleted_at': timezone.now() if customer_status == 'inactive' else None,
                                }
                            )
                            if created:
                                count += 1
                            
                            '''
                            deal = CustomerService(
                                customer = customer,
                                product = 'product',
                                code = poliza,
                                activation_date = datetime.now(),
                                base_premium = 0,
                                provider = company,
                                created_by = request.user,
                                activation_period = 'semi-annual',
                                deactivation_date = expiration,
                                product_status = status
                            )
                            '''
                           
                        messages.add_message(request, messages.SUCCESS, 'Initial data imported successfully. We add ' + str(count) + ' new customers', extra_tags='File_imported success')
                        return redirect(reverse('customers'))
                except:
                    messages.add_message(request, messages.ERROR, 'Error importing data. Please provide all required fields.', extra_tags='Importing_error error')
                    return redirect(reverse('import'))     
            else:
                messages.add_message(request, messages.ERROR, 'Error importing data. Please provide all required fields.', extra_tags='Importing_error error')
                return redirect(reverse('import'))
    
        messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Importing_error error')
        return redirect(reverse('import'))


def split_name(full_name):
    # Dividir la cadena en apellido y nombre usando la coma como separador
    try:
        last_name, first_name = full_name.split(", ")
        last_name = last_name.strip()
        first_name = first_name.strip()
    except:
         first_name = full_name.strip()
         last_name = ''    
    
    return first_name, last_name