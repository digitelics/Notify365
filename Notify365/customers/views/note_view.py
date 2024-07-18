
from django.contrib.auth.decorators import login_required
from security.models import CustomUser as User
from customers.models import Customer, Note
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import datetime


@login_required
def add_note_view(request):
    redirect_tab = 'customer'
    if request.method == 'POST':
        customerId = request.POST.get('customerId')
        note = request.POST.get('note')

        if customerId and note:
            customer = Customer.objects.get(pk=customerId)
           
            note = Note(
                customer = customer,
                note = note,
                date = timezone.now(),
                created_by = request.user,
            )
            note.save()

            messages.add_message(request, messages.SUCCESS, 'Note added successfully.', extra_tags='Note_added success')
            return redirect(reverse('customer_detail', args=[customerId] ))
        else:
            messages.add_message(request, messages.ERROR, 'Error creating note. Please provide all required fields.', extra_tags='Adding_error error')
            return redirect(reverse('customers'))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Adding_error error')
    return redirect(reverse('customers'))
