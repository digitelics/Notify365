from django.shortcuts import render, redirect, get_object_or_404
from settings.models import Provider, State, Product, ProviderType
from security.models import Suscription, CustomUser as Users
from customers.models import Customer, CustomerService
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
import pandas as pd
from django.db import transaction
from datetime import datetime
import re




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
                            address = row['ADDRESS1']
                            importedCity = row['city']
                            PolicyEffective = row['PolicyEffectiveDateTime']
                            premium=row['premium']
                            service = row['lobName']

                            state = get_object_or_404(State, abbreviation='FL')

                            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                            if not re.match(email_regex, email):
                                email = "notemail@notify365.us"
                            

                            if phone:
                                if not phone.startswith('+1') and phone != 'NULL':
                                    phone = '+1' + phone.lstrip('0')
                                else:
                                    phone = '+10000000000'    
                            else:
                                phone = '+10000000000' 

                            if status == "A":  
                                  customer_status = 'client'
                            elif status == "P":
                                 customer_status = 'lead'
                            else:
                                 customer_status = 'inactive'

                            if address == 'NULL' or not address:
                                address = 'Not Address available'

                            if importedCity == 'NULL' or not importedCity:
                                importedCity = 'Not city available'

                            if not poliza:
                                continue

                            

                            customer, created = Customer.objects.get_or_create(
                                first_name=first_name,
                                last_name=last_name,
                                phone=phone,
                                email=email,
                                street = address,
                                city = importedCity,
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
                            
                            ensuranceService, created = Product.objects.get_or_create(
                                name = service, 
                                suscription = request.user.suscription,
                                defaults={
                                    'created_by': request.user,
                                    'created_at': timezone.now(),
                                }
                            )

                            providerType, created = ProviderType.objects.get_or_create(
                                name = 'Initial Data',
                                created_by = request.user,
                                suscription = request.user.suscription,
                                defaults={
                                    'created_at': timezone.now(),
                                }
                            )
                           
                            provider, created = Provider.objects.get_or_create(
                                provider = company,
                                suscription = request.user.suscription,
                                provider_type = providerType,
                                defaults={
                                    'created_by': request.user,
                                    'created_at': timezone.now(),
                                }
                            )

                            if expiration > datetime.now():
                                 product_status = "active"
                            else:
                                 product_status = "inactive"

                            deal, created = CustomerService.objects.get_or_create(
                                customer = customer,
                                product = ensuranceService,
                                code = poliza,
                                activation_date = PolicyEffective,
                                base_premium = premium,
                                provider = provider,
                                activation_period = 'semi-annual',
                                deactivation_date = expiration,
                                product_status = product_status,
                                defaults={
                                    'created_by': request.user,
                                }
                            )
                            
                           
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