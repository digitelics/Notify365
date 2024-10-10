'''
from django.shortcuts import render, redirect
from customers.models import Customer
from notifications.task import send_birthday_notifications, send_document_notifications, send_expiry_notifications, send_next_expiry_notifications, send_expiry_tomorrow_notifications
from django.contrib.auth.decorators import login_required
from notifications.models import Notification
from django.utils import timezone
from utils import send_text_notification
from django.contrib import messages
from django.urls import reverse
from django.conf import settings



def notify(request):
    send_expiry_tomorrow_notifications.delay()
    send_birthday_notifications.delay()
    send_document_notifications.delay()
    send_expiry_notifications.delay()
    send_next_expiry_notifications.delay()
    return render(request, 'notifications/notify_template.html', {})

@login_required
def sms(request, customer_id=None):
    customers = Customer.objects.filter(notifications__channel__in=['text', 'reply']).distinct()
    selected_customer = None

    for customer in customers:
        customer.notifications_list = customer.notifications.filter(channel__in=['text', 'reply']).order_by('-date')
        if customer_id and customer.id == int(customer_id):
            selected_customer = customer

    context = {
        'customers': customers,
        'selected_customer_id': selected_customer.id if selected_customer else None
    }

    return render(request, 'notifications/text_message_template.html', context)


@login_required
def send_message_chat(request):
    if request.method == 'POST':
        customerId = request.POST.get('customer-id')
        message = request.POST.get('message-text')
        attach = request.FILES.get('document-file')
        if customerId and message:
            customer = Customer.objects.get(pk=customerId)
            if attach:
                url = settings.BASE_URL +  "static/files/notification_attach/" + attach.name
                notification = Notification(
                    customer = customer,
                    channel = Notification.TEXT,
                    date = timezone.now(),
                    sent_by = request.user,
                    text = message,
                    attach = attach
                )
                notification.save()
                status = send_text_notification.send_sms(customer.phone, message, url)
            else:
                status = send_text_notification.send_sms(customer.phone, message)
                notification = Notification(
                    customer = customer,
                    channel = Notification.TEXT,
                    date = timezone.now(),
                    sent_by = request.user,
                    text = message,
                    attach = attach
                )
                notification.save()
            if status:
                messages.add_message(request, messages.SUCCESS, 'Message sent successfully.', extra_tags='Message_sent success')
                return redirect(reverse('sms_detail', args=[customerId] ))
            else:
                messages.add_message(request, messages.ERROR, 'Something went wrong. Please contact the system administrator.', extra_tags='Sending_error error')
                return redirect(reverse('sms_detail', args=[customerId] ))
        else:
            messages.add_message(request, messages.ERROR, 'Error sending message. Please provide all required fields.', extra_tags='Sending_error error')
            return redirect(reverse('sms'))

    messages.add_message(request, messages.ERROR, 'Unexpected error. Please try again later.', extra_tags='Sending_error error')
    return redirect(reverse('sms'))

'''

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from customers.models import Customer
from django.contrib.auth.decorators import login_required
from notifications.models import Notification
from django.utils import timezone
from utils import send_text_notification
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
import os
from django.db.models import Max, Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404


login_required
def notify(request):
    '''
    send_expired_service_notifications.delay()
    send_birthday_notifications.delay()
    '''
    calls = Notification.objects.filter(
        Q(channel='call') &
        (
            Q(customer__created_by__suscription=request.user.suscription) |
            Q(to_number=request.user.suscription.company.phone)
        )
    ).order_by('-date')
    
    paginator = Paginator(calls, 10)  # Paginar el queryset con 10 elementos por página
    page_number = request.GET.get('page')  # Obtener el número de página de la solicitud GET
    
    # Obtener la página solicitada o la primera página por defecto
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}  # Pasar el objeto de página al contexto
    
    return render(request, 'notifications/notify_template.html', context)

@login_required
def notify_filter(request):
    phone = request.POST.get('phone-number') or request.GET.get('phone-number')
    
    if phone and phone.isdigit():
        calls = Notification.objects.filter(
            Q(channel='call') &
            (
                # Coincidencia en from_number y verificación del to_number
                (Q(from_number__icontains=phone) & Q(to_number=request.user.suscription.company.phone) &  Q(customer__created_by__suscription=request.user.suscription)) |
                
                # Coincidencia en to_number y verificación del from_number
                (Q(to_number=phone) & Q(from_number=request.user.suscription.company.phone) &  Q(customer__created_by__suscription=request.user.suscription)) 
                
            )
        ).order_by('-date')
    else:
        calls = Notification.objects.filter(
            Q(channel='call') &
            (
                Q(customer__created_by__suscription=request.user.suscription) |
                Q(to_number=request.user.suscription.company.phone)
            )
        ).order_by('-date')
        
    paginator = Paginator(calls, 10)  # Paginar el queryset con 10 elementos por página
    page_number = request.GET.get('page')  # Obtener el número de página de la solicitud GET
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'phone': phone,  # Pasar el valor del filtro al contexto
    }  # Pasar el objeto de página al contexto
    
    return render(request, 'notifications/notify_template.html', context)





@login_required

def sms(request, customer_id=None):
    user = request.user
    suscription = user.suscription

    # Filtramos los clientes con notificaciones de texto o respuesta
    customers = Customer.objects.filter(notifications__channel__in=['text', 'reply']).distinct().annotate(
        latest_notification_date=Max('notifications__date')
    ).order_by('-latest_notification_date')

    customers = customers.filter(created_by__suscription=suscription)

    # Paginamos los clientes
    paginator = Paginator(customers, 10)  # 10 clientes por página
    page_number = int(request.GET.get('page', 1))
    page_obj = paginator.get_page(page_number)

    # Calcular el chatCounter según la página actual
    chat_counter = (page_number - 1) * 10 + 1  # Multiplicamos el número de página por el tamaño de la página para obtener el número inicial

    # Lógica para manejar la selección de un cliente y el renderizado inicial
    selected_customer = None
    for customer in page_obj:
        customer.notifications_list = customer.notifications.filter(channel__in=['text', 'reply']).order_by('-date')
        for notification in customer.notifications_list:
            if notification.attach:
                name, extension = os.path.splitext(notification.attach.name)
                notification.extension = extension
                notification.file_name = os.path.basename(notification.attach.name)
        if customer_id and customer.id == int(customer_id):
            selected_customer = customer
    
    # Si es una solicitud AJAX (scroll infinito)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        
        # Renderizar el template de la lista de clientes y de chats
        customers_html = render_to_string('notifications/customer_list.html', {'customers': page_obj, 'chatCounter': chat_counter})
        chats_html = render_to_string('notifications/chat_list.html', {'customers': page_obj, 'chatCounter': chat_counter})

        return JsonResponse({
            'customers_html': customers_html,  # HTML para los nuevos clientes
            'chats_html': chats_html,  # HTML para los nuevos chats
            'has_next': page_obj.has_next(),
        })

    context = {
        'customers': page_obj,  # Paginación
        'selected_customer_id': selected_customer.id if selected_customer else None,
        'chatCounter': chat_counter  # Pasamos el contador inicial para el template principal
    }

    return render(request, 'notifications/text_message_template.html', context)



@login_required
def load_messages(request, customer_id):
    customer = Customer.objects.get(pk=customer_id)
    notifications = customer.notifications.filter(channel__in=['text', 'reply']).order_by('-date')
    return HttpResponse(render_to_string('notifications/notification_list.html', {'notifications': notifications}))



@login_required
def send_message_chat(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        print('Solicitud AJAX recibida correctamente')
        customer_id = request.POST.get('customer-id')
        message = request.POST.get('message-text')
        attach = request.FILES.get('document-file')

        if customer_id and message:
            try:
                customer = get_object_or_404(Customer, pk=customer_id)
                    
                
               
                if attach:
                    notification = Notification(
                        customer=customer,
                        channel=Notification.TEXT,
                        date=timezone.now(),
                        sent_by=request.user,
                        text=message,
                        created_by=request.user,
                        attach=attach
                    )
                    notification.save()
                    url = settings.BASE_URL + str(notification.attach)
                    print("File URL: "+url)
                    status = send_text_notification.send_sms(customer.phone, message, url)
                else:
                    notification = Notification(
                        customer=customer,
                        channel=Notification.TEXT,
                        date=timezone.now(),
                        sent_by=request.user,
                        created_by=request.user,
                        text=message
                    )
                    notification.save()
                    status = send_text_notification.send_sms(customer.phone, message)
                
                if status != "Error":
                    # Renderizar el nuevo mensaje en HTML para añadirlo al chat sin recargar la página
                    chat_html = render_to_string('notifications/chat_message.html', {
                        'message_text': message,
                        'message_time': timezone.now().strftime('%m/%d/%Y %I:%M %p'),
                        'sent_by_me': True,  # Indicamos que el mensaje es enviado por el usuario actual
                        'attach_url': notification.attach.url if notification.attach else None,
                        'attach_name': os.path.basename(notification.attach.name) if notification.attach else None
                    })
                    return JsonResponse({'html': chat_html})
                else:
                    messages.add_message(request, messages.ERROR, 'Something went wrong. Please contact the system administrator.', extra_tags='Sending_error error')
                    return redirect(reverse('sms'))
            except Exception as e:
                print('Error al procesar el mensaje:', str(e))
                return JsonResponse({'error': 'Error al procesar el mensaje.'}, status=500)
        else:
            return JsonResponse({'error': 'Customer ID and message are required.'}, status=400)
    else:
        print('Solicitud no AJAX detectada o método no permitido')
        return JsonResponse({'error': 'Invalid request. Only AJAX requests are allowed.'}, status=400)