'''
KEYWORDS

<<company>>
<<customer>>
<<documents>>
<<expiry_date>>
<<today>>
<<service>>

'''

import re
from customers.models import CustomerDocument, CustomerService
from datetime import timedelta
from django.utils import timezone


def getText(text, customer, documents=False, expiry_date=False):
    company = customer.created_by.suscription.company
    if documents:
        docs = CustomerDocument.objects.filter(customer=customer.id, created_by__isnull=True)
        doc_names = docs.values_list('document__name', flat=True)
        doc_names_str = ', '.join(doc_names)
    if expiry_date:
        today = timezone.now().date()
        thirty_days_from_now = today + timedelta(days=30)
        deal = CustomerService.objects.filter( customer=customer.id,deactivation_date__gte=today, deactivation_date__lte=thirty_days_from_now).first()
        expiration_date = deal.deactivation_date.strftime('%m-%d-%Y')
        service = deal.product

    replacements = {
        "<<customer>>": f"{customer.first_name}",
        "<<company>>": company.name if company else "Company Name Not Found",
        "<<documents>>": doc_names_str if documents else "Document Name Not Found",
        "<<expiry_date>>": expiration_date if expiry_date else "Expiration date Not Found",
        "<<service>>": f"{service}" if expiry_date else "Product Name Not Found",
    }

    # Función para realizar el reemplazo usando regex
    def replacer(match):
        return replacements.get(match.group(0), match.group(0))

    # Reemplazar todas las ocurrencias de las variables
    pattern = re.compile(r'<<\s*customer\s*>>|<<\s*company\s*>>|<<\s*documents\s*>>|<<\s*expiry_date\s*>>|<<\s*service\s*>>')
    result = pattern.sub(replacer, text)
    print(result)
    return result