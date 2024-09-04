from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard') 
    return render(request, "security/login_template.html", {})

def my_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Autenticar al usuario utilizando authenticate
        user = authenticate(request, username=username, password=password)
        print(user)    
        # Verificar si la autenticación fue exitosa
        if user is not None and user.deleted_at is None:
            # Iniciar sesión del usuario utilizando login
            if user.suscription.expiration_date <= timezone.now().date(): 
                messages.add_message(request, messages.ERROR, 'The subscription for your company has expired. Please contact us to reactivate it.', extra_tags='Subscription_expired error')   
                return redirect('login')
            else:
                auth_login(request, user)
                return redirect('dashboard')  # Redireccionar a la página de inicio o a donde desees
        else:
            messages.add_message(request, messages.ERROR, 'Please check your login data and try again.', extra_tags='Login_error error')   
            return redirect('login')

    messages.add_message(request, messages.ERROR, 'Please check your login data and try again.', extra_tags='Login_error error')   
    return redirect('login')

def responsive_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Autenticar al usuario utilizando authenticate
        user = authenticate(request, username=username, password=password)
        print(user)    
        # Verificar si la autenticación fue exitosa
        if user is not None and user.deleted_at is None:
            # Iniciar sesión del usuario utilizando login
            if user.suscription.expiration_date <= timezone.now().date(): 
                messages.add_message(request, messages.ERROR, 'The subscription for your company has expired. Please contact us to reactivate it.', extra_tags='Subscription_expired error')   
                return redirect('login')
            else:
                auth_login(request, user)
                return redirect('customers')  # Redireccionar a la página de inicio o a donde desees
        else:
            messages.add_message(request, messages.ERROR, 'Please check your login data and try again.', extra_tags='Login_error error')   
            return redirect('login')

    messages.add_message(request, messages.ERROR, 'Please check your login data and try again.', extra_tags='Login_error error')   
    return redirect('login')


def logout_view(request):
    logout(request)
    return redirect('login') 