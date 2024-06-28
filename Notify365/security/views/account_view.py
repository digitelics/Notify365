from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from security.models import CustomUser as User
from django.contrib import messages

# Create your views here.
@login_required
def account(request):
    user = request.user
    context = {
        'user': user.user,
        'name': user.name,
        'phone': user.tel,
        'email': user.email,
        'company': user.suscription.company.name,
        'avatar':user.avatar.url if user.avatar else '',
        'id': user.id,
    }
    return render(request, "security/account_template.html", {'data':context})


# Edit Company
@login_required
def edit_account(request):
    user = request.user
    account_to_edit = User.objects.get(pk=user.id)

    if request.method == 'POST':
        # Obtener los datos enviados por el formulario
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        avatar = request.FILES.get('user-photo')  # Handle file upload

        if not all([name, email, phone]):
            messages.add_message(request, messages.ERROR, 'All fields are required.', extra_tags='Updating_error error')
            return redirect('account')
        else:
            account_to_edit.name = name
            account_to_edit.email = email
            account_to_edit.tel = phone
            if avatar:
                account_to_edit.avatar = avatar
            account_to_edit.save()

            messages.add_message(request, messages.SUCCESS, 'Account information updated successfully.', extra_tags='Account_updated success')
            return redirect('account') 

    # Si el método no es POST, renderiza el formulario con los datos actuales
    
    messages.add_message(request, messages.ERROR, "Sorry, we can't complete this transaction.", extra_tags='Editing_error error')
    return redirect('account') 