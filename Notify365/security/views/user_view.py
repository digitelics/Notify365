from django.shortcuts import redirect
from django.views.generic import ListView
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from security.models import CustomUser as User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone


# List Users
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'security/users_template.html'
    context_object_name = 'page_obj'  # Este es el nombre de la variable en la plantilla

    def get_queryset(self):
        current_date = timezone.now().date()
        if self.request.user.is_superuser:
            users = User.objects.filter(
                suscription__is_active=True,
                suscription__expiration_date__gte=current_date,
                deleted_at__isnull=True
            ).order_by('-created_at')
        else:
            user_suscription = self.request.user.suscription
            users = User.objects.filter(
                suscription=user_suscription,
                suscription__is_active=True,
                suscription__expiration_date__gte=current_date,
                deleted_at__isnull=True
            ).order_by('-created_at')

        paginator = Paginator(users, 10)  # Paginar el queryset con 10 elementos por página
        page_number = self.request.GET.get('page')  # Obtener el número de página de la solicitud GET

        # Obtener la página solicitada o la primera página por defecto
        page_obj = paginator.get_page(page_number)

        return page_obj  # Devolver el objeto paginado en lugar del queryset

        
        
# Create User
login_required
def create_user(request):

    if request.method == 'POST':
        password = request.POST.get('password')
        name = request.POST.get('name')
        email = request.POST.get('email')
        tel = request.POST.get('phone')
        avatar = request.FILES.get('avatar')  # Handle file upload
        
        try:
            user = User.objects.get(email=email)
            messages.add_message(request, messages.ERROR, 'The user you are trying to add already exists.', extra_tags='User_exist error')
            return redirect('users')
        except:
           pass

        if not all([password, name, email, tel]):
            messages.add_message(request, messages.ERROR, 'All fields are required.', extra_tags='Creation_error error')
            return redirect('users')
        else:   
            # Get the logged-in user's subscription
            suscription = request.user.suscription
            allowed_users = suscription.max_users - User.objects.filter(suscription=suscription.id, deleted_at=None).count()
            print(allowed_users)
            if allowed_users <= 0:
                messages.add_message(request, messages.ERROR, 'You have used all available users in your subscription. To create more users, please upgrade your plan.', extra_tags='Adding_error error')
                return redirect('users')
            
            # Create the user
            new_user = User.objects.create(
                user = email,
                password = make_password(password),
                name = name,
                email = email,
                tel = tel,
                suscription = suscription,
                avatar = avatar,
                created_by = request.user,
                created_at = timezone.now()
            )
            new_user.save()
            messages.add_message(request, messages.SUCCESS, 'User created successfully.', extra_tags='User_created success')
            return redirect('users')
    
    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Adding_error error')
    return redirect('users')


# Edit User
@login_required
def edit_user(request, user_id):
    # Obtener el usuario que se va a editar
    user_to_edit = User.objects.get(pk=user_id)

    if request.method == 'POST':
        # Obtener los datos enviados por el formulario
        name = request.POST.get('name')
        email = request.POST.get('email')
        tel = request.POST.get('phone')
        avatar = request.FILES.get('avatar')  # Handle file upload
        
        # Validar que el correo electrónico no esté siendo utilizado por otro usuario
        if email != user_to_edit.email and User.objects.filter(email=email).exists():
            messages.add_message(request, messages.ERROR, 'This email address is already in use.', extra_tags='Update_error error')
            return redirect('users')

        # Actualizar los datos del usuario
        user_to_edit.name = name
        user_to_edit.email = email
        user_to_edit.tel = tel
        if avatar:
            user_to_edit.avatar = avatar
        user_to_edit.save()

        messages.add_message(request, messages.SUCCESS, 'User information updated successfully.', extra_tags='User_updated success')
        return redirect('users')
    
    messages.add_message(request, messages.WARNING, "We can't find that User.", extra_tags='Alert! warning')
    return redirect('users')

# Reset Password
@login_required
def reset_password(request, user_id):
    # Obtener el usuario que se va a editar
    user_to_reset_password = User.objects.get(pk=user_id)

    if request.method == 'POST':
        # Obtener los datos enviados por el formulario
        password = request.POST.get('password')
        if not all([password]):
            messages.add_message(request, messages.ERROR, "Password can't be blank.", extra_tags='Validation_error error')
            return redirect('users')

        # Actualizar los datos del usuario
        user_to_reset_password.password = make_password(password)
        user_to_reset_password.save()

        messages.add_message(request, messages.SUCCESS, 'Password updated successfully.', extra_tags='Password_updated success')
        return redirect('users')
    
    messages.add_message(request, messages.WARNING, "We can't find that User.", extra_tags='Alert! warning')
    return redirect('users')


# Reset Password
@login_required
def delete_user(request, user_id):
    # Obtener el usuario que se va a editar
    user_to_delete = User.objects.get(pk=user_id)

    if request.method == 'POST':
        
        # Actualizar los datos del usuario
        user_to_delete.deleted_at = timezone.now()
        user_to_delete.save()

        messages.add_message(request, messages.SUCCESS, 'User delete successfully.', extra_tags='Delete_user success')
        return redirect('users')
    
    messages.add_message(request, messages.WARNING, "We can't find that User.", extra_tags='Alert! warning')
    return redirect('users')