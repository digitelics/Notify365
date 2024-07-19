from django.contrib.auth.decorators import login_required
from security.models import CustomUser as User
from customers.models import Customer, CustomerService, CustomerDocument
from settings.models import Product, RequiredDocument
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from django.db import transaction

@login_required
def add_deal_view(request):
    redirect_tab = 'customer'
    if request.method == 'POST':
        customerId = request.POST.get('customerId')
        productId = request.POST.get('service')
        base_premium = request.POST.get('dealamount')
        product_classification = request.POST.get('type')
        activation_date_str = request.POST.get('activation_date')
        activation_period = request.POST.get('activation_true')
        code = request.POST.get('code')

        if customerId and productId:
            try:
                with transaction.atomic():
                    customer = Customer.objects.get(pk=customerId)
                    product = Product.objects.get(pk=productId)
                    activation_date = datetime.strptime(activation_date_str, '%Y-%m-%d').date()

                    customer.customer_status = Customer.CLIENTE
                    customer.save()
                    
                    service = CustomerService(
                        customer=customer,
                        product=product,
                        base_premium=base_premium,
                        product_classification=product_classification,
                        activation_date=activation_date,
                        activation_period=activation_period,
                        code=code,
                        created_by=request.user,
                        created_at=timezone.now(),
                        product_status=CustomerService.ACTIVE
                    )
                    service.save()

                    # Guardar los documentos asociados al producto si no existen para el cliente
                    documents = product.documents.all()
                    for document in documents:
                        if not CustomerDocument.objects.filter(customer=customer, document=document).exists():
                            customer_document = CustomerDocument(
                                customer=customer,
                                document=document,
                                created_at=timezone.now()
                            )
                            customer_document.save()

                    messages.add_message(request, messages.SUCCESS, 'Deal added successfully.', extra_tags='Deal_added success')
                    return redirect(reverse('customer_detail', args=[customerId]))

            except Exception as e:
                messages.add_message(request, messages.ERROR, f'Error creating deal: {e}', extra_tags='Adding_error error')
                return redirect(reverse('customers'))
        else:
            messages.add_message(request, messages.ERROR, 'Error creating deal. Please provide all required fields.', extra_tags='Adding_error error')
            return redirect(reverse('customers'))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Adding_error error')
    return redirect(reverse('customers'))
