from django.views.generic import TemplateView
from settings.models import ProviderType, TemplateCategory, RequiredDocument, Product
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
import json


# List all content geral tab
@method_decorator(login_required, name='dispatch')
class GeneralSettingView(TemplateView):
    template_name = 'settings/general_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_subscription = self.request.user.suscription

        tab = kwargs.get('tab', 'general')
        context['tab'] = tab

        if tab == 'general':
            context['provider_types'] = ProviderType.objects.filter(suscription = user_subscription, deleted_at=None)
            context['template_categories'] = TemplateCategory.objects.filter(suscription = user_subscription, deleted_at=None)
            context['required_documents'] = RequiredDocument.objects.filter(suscription = user_subscription, deleted_at=None)
        elif tab == 'product':
            products = Product.objects.filter(suscription = user_subscription, deleted_at=None).order_by('name')
            documents = RequiredDocument.objects.filter(suscription = user_subscription, deleted_at=None)
            documents_list = list(documents.values('id', 'name'))  
            documents_json = json.dumps(documents_list)  
            context['products'] = products
            context['documents'] = documents
            context['documents_json'] = documents_json
            paginator = Paginator(products, 10) 
            page_number = self.request.GET.get('page')  
            context['page_obj'] = paginator.get_page(page_number)
     
        return context
  
# --------------------------------------------- Template Category ------------------------------------ #
    
@login_required
def add_template_category(request):
    if request.method == 'POST':
        name = request.POST.get('category-name')
        description = request.POST.get('description')
        redirect_tab = 'general'  
        if name:
            template_category = TemplateCategory.objects.create(
                name=name,
                description=description,
                created_by=request.user,
                suscription=request.user.suscription  
            )
            messages.add_message(request, messages.SUCCESS, 'Template category created successfully.', extra_tags='Template_category_created success')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
        else:
            messages.add_message(request, messages.ERROR, 'Error creating template category. Please provide all required fields.', extra_tags='Adding_error error')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    
    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Adding_error error')
    return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))

@login_required
def edit_template_category(request, id):
    template_category = get_object_or_404(TemplateCategory, pk=id)
    redirect_tab = 'general'  
    if request.method == 'POST':
        name = request.POST.get('edit-category-name')
        description = request.POST.get('edit-description')
        
        if name:
            template_category.name = name
            template_category.description = description
            template_category.save()
            messages.success(request, 'Template category updated successfully.', extra_tags='Update_template_category success')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
        else:
            messages.error(request, 'Error updating template category. Please provide all required fields.', extra_tags='Updating_error error')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    
    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Updating_error error')
    return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))


@login_required
def delete_template_category(request, id):
    template_category = get_object_or_404(TemplateCategory, pk=id)
    redirect_tab = 'general'  
    if request.method == 'POST':
        template_category.deleted_at = timezone.now()
        template_category.save()
        messages.success(request, 'Template category deleted successfully.', extra_tags='Delete_template_category success')
        return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    else:
        messages.error(request, 'Unexpected error. Please try again later.', extra_tags='Delete_error error')
        return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))


# --------------------------------------------- Provider type -------------------------------------- #
    
@login_required
def add_provider_type(request):
    if request.method == 'POST':
        name = request.POST.get('provider-type')
        description = request.POST.get('description')
        redirect_tab = 'general'
        if name:
            provider_type = ProviderType.objects.create(
                name=name,
                description=description,
                created_by=request.user,
                suscription=request.user.suscription  
            )
            messages.add_message(request, messages.SUCCESS, 'Provider type created successfully.', extra_tags='Provider_type_created success')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
        else:
            messages.add_message(request, messages.ERROR, 'Error creating Provider type. Please provide all required fields.', extra_tags='Adding_error error')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    
    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Adding_error error')
    return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))

@login_required
def edit_provider_type(request, id):
    type = get_object_or_404(ProviderType, pk=id)
    redirect_tab = 'general'  
    if request.method == 'POST':
        name = request.POST.get('edit-provider-type')
        description = request.POST.get('edit-provider-type-description')
        
        if name:
            type.name = name
            type.description = description
            type.save()
            messages.success(request, 'Provider type updated successfully.', extra_tags='Update_provider_type success')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
        else:
            messages.error(request, 'Error updating provider type . Please provide all required fields.', extra_tags='Updating_error error')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    
    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Updating_error error')
    return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))


@login_required
def delete_provider_type(request, id):
    type = get_object_or_404(ProviderType, pk=id)
    redirect_tab = 'general'  
    if request.method == 'POST':
        type.deleted_at = timezone.now()
        type.save()
        messages.success(request, 'Provider type  deleted successfully.', extra_tags='Delete_provider_type success')
        return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    else:
        messages.error(request, 'Unexpected error. Please try again later.', extra_tags='Delete_error error')
        return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))


# --------------------------------------------- Required document -------------------------------------- #
    
@login_required
def add_required_document(request):
    if request.method == 'POST':
        name = request.POST.get('document-name')
        description = request.POST.get('description')
        redirect_tab = 'general'
        if name:
            required_document = RequiredDocument.objects.create(
                name=name,
                description=description,
                created_by=request.user,
                suscription=request.user.suscription  
            )
            messages.add_message(request, messages.SUCCESS, 'Document created successfully.', extra_tags='Document_created success')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
        else:
            messages.add_message(request, messages.ERROR, 'Error creating Required document. Please provide all required fields.', extra_tags='Adding_error error')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    
    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Adding_error error')
    return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))

@login_required
def edit_required_document(request, id):
    document = get_object_or_404(RequiredDocument, pk=id)
    redirect_tab = 'general'  
    if request.method == 'POST':
        name = request.POST.get('document-name')
        description = request.POST.get('description')
        
        if name:
            document.name = name
            document.description = description
            document.save()
            messages.success(request, 'Required document updated successfully.', extra_tags='Update_required_document success')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
        else:
            messages.error(request, 'Error updating Required document . Please provide all required fields.', extra_tags='Updating_error error')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    
    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Updating_error error')
    return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))


@login_required
def delete_required_document(request, id):
    required_document = get_object_or_404(RequiredDocument, pk=id)
    redirect_tab = 'general'  
    if request.method == 'POST':
        required_document.deleted_at = timezone.now()
        required_document.save()
        messages.success(request, 'Required document  deleted successfully.', extra_tags='Delete_required_document success')
        return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    else:
        messages.error(request, 'Unexpected error. Please try again later.', extra_tags='Delete_error error')
        return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))


