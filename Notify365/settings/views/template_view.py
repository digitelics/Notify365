from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from notifications.models import Template
from security.models import Suscription
from settings.models import RequiredDocument
from django.urls import reverse
from django.contrib.auth.decorators import login_required



@login_required
def add_template_view(request):
    redirect_tab = 'mt'
    if request.method == 'POST':
        name = request.POST.get('add-template-name')
        text = request.POST.get('add-template-text')
        type = request.POST.get('add-template-type') 
        channel = request.POST.get('add-template-channel') 
       
        # Fetching suscription
        suscription = request.user.suscription  
        if name and text and type and channel:
            # Creating the template
            template, created = Template.objects.update_or_create(
                suscription=suscription, 
                type=type, 
                channel_to=channel,
                defaults={
                    'name': name,
                    'text': text,
                    'created_at': timezone.now(),
                    'created_by': request.user,
                }
            )
            

            messages.add_message(request, messages.SUCCESS, 'Template added successfully.', extra_tags='Template_added success')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
        else:
            messages.add_message(request, messages.ERROR, 'Error creating template. Please provide all required fields.', extra_tags='Adding_error error')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    
    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Adding_error error')
    return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))


@login_required
def edit_template_view(request, id):
    template = get_object_or_404(Template, pk=id)
    redirect_tab = 'mt'
    if request.method == 'POST':
        name = request.POST.get('edit-template-name')
        text = request.POST.get('edit-template-text')

        if name and text:
            template.name = name
            template.text = text
            template.updated_at = timezone.now()
            template.save()
            
            messages.add_message(request, messages.SUCCESS, 'Template updated successfully.', extra_tags='Template_updated success')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
        else:
            messages.add_message(request, messages.ERROR, 'Error updating Template. Please provide all required fields.', extra_tags='Updating_error error')
            return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Updating_error error')
    return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))


@login_required
def delete_template(request, id):
    template = get_object_or_404(Template, pk=id)
    redirect_tab = 'mt'  
    if request.method == 'POST':
        template.deleted_at = timezone.now()
        template.save()
        messages.success(request, 'Template deleted successfully.', extra_tags='Delete_template success')
        return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
    else:
        messages.error(request, 'Unexpected error. Please try again later.', extra_tags='Delete_error error')
        return redirect(reverse('general_setting', kwargs={'tab': redirect_tab}))
