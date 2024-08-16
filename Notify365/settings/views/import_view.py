from django.shortcuts import render, redirect
from settings.models.company_model import Company, State
from security.models import Suscription, CustomUser as Users
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
            
            if excel_file:
                try:
                    # Read the Excel file using pandas
                    df = pd.read_excel(excel_file)

                    with transaction.atomic():
                        for _, row in df.iterrows():
                            # Save data to the Provider model
                            provider_instance = Company(
                                provider=row['provider'],
                                suscription=row['suscription'],
                                created_at=datetime.now(),
                                deleted_at=row.get('deleted_at'),  # Assuming it's optional
                                history=row.get('history'),  # Assuming it's optional
                                created_by=request.user,
                                ProviderType=row['ProviderType']
                            )
                            provider_instance.save()
                            messages.add_message(request, messages.SUCCESS, 'Initial data imported successfully.', extra_tags='File_imported success')
                            return redirect(reverse('dashboard'))
                except:
                    messages.add_message(request, messages.ERROR, 'Error importing data. Please provide all required fields.', extra_tags='Importing_error error')
                    return redirect(reverse('import'))     
            else:
                messages.add_message(request, messages.ERROR, 'Error importing data. Please provide all required fields.', extra_tags='Importing_error error')
                return redirect(reverse('import'))
    
        messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Importing_error error')
        return redirect(reverse('import'))