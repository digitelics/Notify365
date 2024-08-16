
'''
THE DOCUMENT CREATION IS AT THE MOMENT WHEN THE USER ADD A NEW SERVICE HERE YOU CAN FIND ONLY THE UPDATE AND DELETE DOCUMENT
'''

from django.contrib.auth.decorators import login_required
from customers.models import Customer, CustomerDocument
from settings.models import RequiredDocument
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone


@login_required
def update_document_view(request):
    redirect_tab = 'customer'
    if request.method == 'POST':
        customerId = request.POST.get('customerId')
        document = request.POST.get('customer-document')
        filedescription = request.POST.get('filedescription')
        documentFile = request.FILES.get('document-file')
        if document and documentFile:
            try:
                customerDocument = CustomerDocument.objects.get(document=document, customer=customerId)
                customerDocument.description = filedescription
                customerDocument.doc_path = documentFile
                customerDocument.created_by = request.user
                customerDocument.save()
                messages.add_message(request, messages.SUCCESS, 'Document uploaded successfully.', extra_tags='Document_uploaded success')
                return redirect(reverse('customer_detail', args=[customerId] ))
            except:
                document = RequiredDocument.objects.get(pk=document)
                customer = Customer.objects.get(pk=customerId)
                customerDocument = CustomerDocument(
                    description = filedescription,
                    doc_path =  documentFile,
                    created_by = request.user,
                    document = document,
                    customer = customer,
                )
                customerDocument.save()
                messages.add_message(request, messages.SUCCESS, 'Document uploaded successfully.', extra_tags='Document_uploaded success')
                return redirect(reverse('customer_detail', args=[customerId] ))

           
        else:
            messages.add_message(request, messages.ERROR, 'Error uploading document. Please provide all required fields.', extra_tags='Uploading_error error')
            return redirect(reverse('customers'))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Uploading_error error')
    return redirect(reverse('customers'))
