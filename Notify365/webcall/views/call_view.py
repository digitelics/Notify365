from django.shortcuts import render

from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.twiml.messaging_response import MessagingResponse
from django.core.files.base import ContentFile
import requests
import time

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from notifications.models import Notification
from customers.models import Customer
from django.utils import timezone
from mimetypes import guess_extension
from security.models import Suscription, CustomUser as User
from django.contrib.sessions.models import Session

#from dotenv import load_dotenv
import os

from dotenv import load_dotenv
load_dotenv()


TWIML_APP_SID= os.getenv('TWIML_APP_SID')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_API_KEY_SID = os.getenv('TWILIO_API_KEY_SID')
TWILIO_API_KEY_SECRET = os.getenv('TWILIO_API_KEY_SECRET')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')



def home(request):
    return render(request, 'webcall/home.html', {})


@csrf_exempt
def get_token(request):
    identity = TWILIO_NUMBER
    outgoing_application_sid = TWIML_APP_SID

    access_token = AccessToken(TWILIO_ACCOUNT_SID, TWILIO_API_KEY_SID, TWILIO_API_KEY_SECRET, identity=identity)

    voice_grant = VoiceGrant(outgoing_application_sid=outgoing_application_sid, incoming_allow=True)
    access_token.add_grant(voice_grant)

    token = access_token.to_jwt()
    identity = identity

    data = {'token': token, 'identity': identity}
    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'

    return response


@csrf_exempt
def call(request):
    response = VoiceResponse()
    to_number = request.POST.get('To')
    print(to_number)
    if to_number and to_number != TWILIO_NUMBER:
        print('outbound call')
        dial = Dial(record="record-from-answer", caller_id=TWILIO_NUMBER)
        dial.number(to_number)
        #response.record(max_length=120, action='/webcall/handle_recording/')
    else:
        print('incoming call')
        if not get_available_agents(to_number):  # Verifica la disponibilidad de agentes
            response.say("Lo siento, no hay agentes disponibles en este momento. Por favor, deje su mensaje después del tono.", language="es-ES")
            response.record(max_length=120, action='/webcall/handle_recording/')
        else:
            dial = Dial(record="record-from-answer", caller_id=TWILIO_NUMBER)
            dial.client(TWILIO_NUMBER)
            response.append(dial)
            #response.record(max_length=120, action='/webcall/handle_recording/')

    return HttpResponse(str(response), content_type='text/xml')

def get_available_agents(company_phone):
    active_user_ids = get_active_sessions()
    # Filtrar usuarios que son agentes y que tienen sesiones activas
    available_agents = User.objects.filter(id__in=active_user_ids, is_agent=True).first()
    if available_agents:
        return True
    return False

def get_active_sessions():
    # Obtener sesiones que no han expirado
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    # Extraer IDs de usuarios de las sesiones activas
    active_user_ids = [session.get_decoded().get('_auth_user_id') for session in active_sessions]
    return active_user_ids

@csrf_exempt
def handle_recording(request):
    if request.method == 'POST':
        recording_url = request.POST.get('RecordingUrl')
        to_number = request.POST.get('To', '')
        from_number = request.POST.get('From')
        media_content_type = request.POST.get('MediaContentType')
        call_duration = request.POST.get('CallDuration')  # Duración de la llamada en segundos
        call_direction = request.POST.get('Direction')  # Dirección de la llamada (inbound/outbound)

        print(f"Recording URL: {recording_url}")
        print(f"From number: {from_number}")
        print(f"Media content type: {media_content_type}")

        if not recording_url or not from_number:
            return HttpResponse("Missing recording URL or from number.", status=400)

        # Esperar 5 segundos antes de intentar recuperar la grabación
        time.sleep(5)

        response = requests.get(recording_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        print(f"Recording fetch status code: {response.status_code}")

        if response.status_code != 200:
            return HttpResponse(f"Failed to fetch recording. Status code: {response.status_code}", status=500)
       
        customer = Customer.objects.filter(phone=from_number).first()
        print(f"Customer: {customer}")

        if media_content_type:
            extension = guess_extension(media_content_type)
        else:
            extension = ".mp3"  # Default to .mp3 if media content type is not provided

        file_name = f"{recording_url.split('/')[-1]}{extension}"
        print("File name: " + file_name)
        content_file = ContentFile(response.content, name=file_name)

        notification = Notification(
            text=call_direction,
            customer=customer if customer else None,
            date=timezone.now(),
            channel=Notification.CALL,
            sent_by="Customer Call",
            read=False,
            attach=content_file,
            to_number=to_number,
            from_number = from_number
        )
        notification.save()
        return HttpResponse("Recording saved.")
    else:
        return HttpResponseNotAllowed(['POST'])
    
@csrf_exempt
def save_log_call(request):
    try:
        user = request.user
    except:
        user = None
    if request.method == 'POST':
        try:
            phoneNumber = request.POST.get('fromNumber', '')
            toNumber = request.POST.get('toNumber', '')
            customer = Customer.objects.get(phone=phoneNumber)
        except:
            customer = None
        print('este es el numero:' + phoneNumber)
        duration = request.POST.get('duration', '')
        direction = request.POST.get('direction', '')
        text = 'The ' + direction + ' call lasted ' + duration
       
        return JsonResponse({'message': 'Registro de llamada guardado exitosamente'})
    
    # Manejar otros métodos de solicitud si es necesario
    return JsonResponse({'error': 'Solicitud no válida'}, status=400)

@csrf_exempt   
def sms_reply(request):
    from_number = request.POST.get('From')
    customer = Customer.objects.filter(phone=from_number).first()
    body = request.POST.get('Body')
    
    # Crear la notificación inicial sin el archivo adjunto
    notification = Notification(
        text=body,
        customer=customer,
        date=timezone.now(),
        channel=Notification.REPLY,
        sent_by="Customer Message",
        read=False,
    )
    notification.save()
    
    # Procesar archivos adjuntos
    num_media = int(request.POST.get('NumMedia', 0))
    print("Atach count: "+ str(num_media))
    for i in range(num_media):
        media_url = request.POST.get(f'MediaUrl{i}')
        print("Media URL: " + media_url)
        media_content_type = request.POST.get(f'MediaContentType{i}')
        
        # Descargar el archivo adjunto
        response = requests.get(media_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        if response.status_code == 200:
            extension = guess_extension(media_content_type)
            file_name = f"{media_url.split('/')[-1]}{extension}"
            print("File name: "+file_name)
            content_file = ContentFile(response.content)

            if i == 0:
                # Adjuntar el primer archivo a la notificación inicial
                notification.attach.save(file_name, content_file)
            else:
                # Crear nuevas notificaciones para los archivos adicionales
                additional_notification = Notification(
                    text="Attached file",
                    customer=customer,
                    date=timezone.now(),
                    channel=Notification.REPLY,
                    sent_by="Customer Message",
                    read=False,
                )
                additional_notification.attach.save(file_name, content_file)
                additional_notification.save()

    # Responder al mensaje
    response = MessagingResponse()
    if 'stop' in body.lower():
        customer.do_not_disturb  = True
        customer.save()
        response.message("We have received your request, and you have been unsubscribed from our notifications. If you change your mind or need assistance in the future, feel free to contact us. Thank you!")
    else:
        response.message("Gracias por tu mensaje. Pronto te responderemos.")
    return HttpResponse(str(response), content_type='text/xml')


@csrf_exempt
@login_required
def check_number(request):
    if request.method == "POST":
        to_number = request.POST.get('to_number')
        user = request.user
        subscription = user.suscription
        is_configured = Suscription.objects.filter(pk=subscription.id, company__phone=to_number).exists()
        return JsonResponse({'is_configured': is_configured})