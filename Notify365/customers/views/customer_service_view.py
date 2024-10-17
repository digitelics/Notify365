from django.contrib.auth.decorators import login_required
from security.models import CustomUser as User
from customers.models import Customer, CustomerService, CustomerDocument, PremiumTransaction
from settings.models import Product, RequiredDocument, Provider
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
        providerId = request.POST.get('provider')

        if customerId and productId:
            try:
                with transaction.atomic():
                    customer = Customer.objects.get(pk=customerId)
                    product = Product.objects.get(pk=productId)
                    provider = Provider.objects.get(pk=providerId)
                    activation_date = datetime.strptime(activation_date_str, '%Y-%m-%d').date()

                    customer.customer_status = Customer.CLIENT
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
                        product_status=CustomerService.ACTIVE,
                        provider = provider,
                    )
                    service.save()

                    premium_transaction = PremiumTransaction(
                        deal = service,
                        premium = base_premium,
                        type = 'writer',
                        created_by = request.user
                    )
                    premium_transaction.save()

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



@login_required
def edit_deal_view(request, id):
    redirect_tab = 'customer'
    if request.method == 'POST':
        customerId = request.POST.get('customerId')
        base_premium = request.POST.get('edit-dealamount')
        product_classification = request.POST.get('edit-type')
        activation_date_str = request.POST.get('edit-activation-date')
        activation_period = request.POST.get('edit-activation_true')
        code = request.POST.get('edit-code')
        providerId = request.POST.get('edit-provider')
        detail = request.POST.get('edit-details')

        if id:
            try:
                with transaction.atomic():
                    provider = Provider.objects.get(pk=providerId)
                    user = User.objects.get(pk=request.user.id)
                    service = CustomerService.objects.get(pk=id)
                    if activation_date_str:
                        activation_date_str = activation_date_str.strip()
                        activation_date = datetime.strptime(activation_date_str, '%Y-%m-%d').date()
                        service.activation_date=activation_date
                    service.base_premium=base_premium
                    service.product_classification=product_classification
                    service.activation_period=activation_period
                    service.code=code
                    service.created_by=user
                    service.product_status=CustomerService.ACTIVE
                    service.provider = provider
                    service.notes = detail
                    service.save()

                    # Obtener o crear una instancia de PremiumTransaction
                    premium_transaction, created = PremiumTransaction.objects.get_or_create(
                        deal=service,  # Buscar por la relación con el deal
                        defaults={
                            'premium': base_premium,  # Valor por defecto para la creación
                            'created_by': user,       # Valor por defecto para la creación
                            'type': PremiumTransaction.PREMIUM_WRITER,  # Valor por defecto
                        }
                    )

                    # Si la transacción ya existía, actualizamos los campos que correspondan
                    if not created:
                        premium_transaction.premium = base_premium  # Actualizar si es necesario
                        premium_transaction.created_by = user
                        premium_transaction.save()  # Guardar los cambios
                                        
                    messages.add_message(request, messages.SUCCESS, 'Deal updated successfully.', extra_tags='Deal_updated success')
                    return redirect(reverse('customer_detail', args=[service.customer.id]))

            except Exception as e:
                messages.add_message(request, messages.ERROR, f'Error updating deal: {e}', extra_tags='Updating_error error')
                return redirect(reverse('customers'))
        else:
            messages.add_message(request, messages.ERROR, 'Error updating deal. Please provide all required fields.', extra_tags='Updating_error error')
            return redirect(reverse('customers'))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Adding_error error')
    return redirect(reverse('customers'))


@login_required
def cancel_deal_view(request, id):
    if request.method == 'POST':
        dealID = request.POST.get('customerId')
        cancelPremium = request.POST.get('cancel-dealamount')
        detail = request.POST.get('cancel-details')

        if id and cancelPremium:
            try:
                with transaction.atomic():
                    customerService = CustomerService.objects.get(pk=id)
                    customerService.notes = detail
                    customerService.product_status = 'inactive'
                    customerService.save()

                    premium_transaction = PremiumTransaction(
                        deal = customerService,
                        premium = cancelPremium,
                        type = 'cancel',
                        created_by = request.user
                    )
                    premium_transaction.save()

                    messages.add_message(request, messages.SUCCESS, 'Deal canceled successfully.', extra_tags='Deal_canceled success')
                    return redirect(reverse('customer_detail', args=[customerService.customer.id]))

            except Exception as e:
                messages.add_message(request, messages.ERROR, f'Error canceling deal: {e}', extra_tags='Canceling_error error')
                return redirect(reverse('customers'))
        else:
            messages.add_message(request, messages.ERROR, 'Error canceling deal. Please provide all required fields.', extra_tags='Canceling_error error')
            return redirect(reverse('customers'))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Canceling_error error')
    return redirect(reverse('customers'))


@login_required
def delete_deal_view(request, id):
    if request.method == 'POST':
        dealID = request.POST.get('customerId')
        if id:
            try:
                with transaction.atomic():
                    customerService = CustomerService.objects.get(pk=id)
                    customerService.deleted_at = timezone.now()
                    customerService.product_status = 'inactive'
                    customerService.save()

                    premiumTransaction = PremiumTransaction.objects.get(deal=id)
                    premiumTransaction.delete()

                    documets = Product.objects.get(pk=customerService.product.id).documents.all()
                    for document in documets:
                        try:    
                            customerDocument = CustomerDocument.objects.get(document=document.id, customer=customerService.customer.id)
                            if customerDocument.created_by == None:
                                customerDocument.delete()
                        except:
                            continue

                    messages.add_message(request, messages.SUCCESS, 'Deal deleted successfully.', extra_tags='Deal_deleted success')
                    return redirect(reverse('customer_detail', args=[customerService.customer.id]))

            except Exception as e:
                messages.add_message(request, messages.ERROR, f'Error deleting deal: {e}', extra_tags='Deleting_error error')
                return redirect(reverse('customers'))
        else:
            messages.add_message(request, messages.ERROR, 'Error deleting deal. Please provide all required fields.', extra_tags='Deleting_error error')
            return redirect(reverse('customers'))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Canceling_error error')
    return redirect(reverse('customers'))
