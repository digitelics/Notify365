from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from settings.models import Product
from security.models import Suscription
from settings.models import RequiredDocument
from django.urls import reverse
from django.contrib.auth.decorators import login_required



@login_required
def add_product_view(request):
    redirect_tab = 'product'
    if request.method == 'POST':
        name = request.POST.get('product-name')
        description = request.POST.get('add-product-description')
        documents = request.POST.getlist('documents')  # Assuming documents are sent as a list of IDs
        

        # Fetching suscription
        suscription = request.user.suscription  
        if name:
            # Creating the product
            product = Product.objects.create(
                name=name,
                description=description,
                suscription=suscription,
                created_by=request.user,
            )
            
            # Adding documents to the product
            for doc_id in documents:
                document = get_object_or_404(RequiredDocument, pk=doc_id)
                product.documents.add(document)

            product.save()

            messages.add_message(request, messages.SUCCESS, 'Product added successfully.', extra_tags='product_added success')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
        else:
            messages.add_message(request, messages.ERROR, 'Error creating product. Please provide all required fields.', extra_tags='Adding_error error')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    
    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Adding_error error')
    return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))


@login_required
def edit_product_view(request, id):
    product = get_object_or_404(Product, pk=id)
    redirect_tab = 'product'
    if request.method == 'POST':
        name = request.POST.get('edit-product-name')
        if name:
            product.name = name
            product.description = request.POST.get('edit-product-description')
            documents = request.POST.getlist('documents')
            
            # Clearing and updating documents
            product.documents.clear()
            for doc_id in documents:
                document = get_object_or_404(RequiredDocument, pk=doc_id)
                product.documents.add(document)
            
            product.save()
            messages.add_message(request, messages.SUCCESS, 'Product updated successfully.', extra_tags='product_updated success')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
        else:
            messages.add_message(request, messages.ERROR, 'Error updating product. Please provide all required fields.', extra_tags='Updating_error error')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Updating_error error')
    return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))


@login_required
def delete_product(request, id):
    product = get_object_or_404(Product, pk=id)
    redirect_tab = 'product'  
    if request.method == 'POST':
        product.deleted_at = timezone.now()
        product.save()
        messages.success(request, 'Product deleted successfully.', extra_tags='Delete_product success')
        return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    else:
        messages.error(request, 'Unexpected error. Please try again later.', extra_tags='Delete_error error')
        return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
