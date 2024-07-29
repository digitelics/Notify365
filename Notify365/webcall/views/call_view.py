from django.shortcuts import render

from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.twiml.messaging_response import MessagingResponse

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from notifications.models import Notification
from customers.models import Customer
from django.utils import timezone

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

    # Obtiene los datos del cuerpo de la solicitud HTTP
    caller = request.POST.get('Caller', '')

    response = VoiceResponse()
    dial = Dial(caller_id=TWILIO_NUMBER)  # 'callerId' ha sido cambiado a 'caller_id' en la versión actual de Twilio

    to_number = request.POST.get('To', '')

    if to_number and to_number != TWILIO_NUMBER:
        print('outbound call')
        dial.number(to_number)
    else:
        print('incoming call')
        dial = Dial(caller_id=caller)  # Se cambió el valor de 'dial' si es una llamada entrante
        dial.client(TWILIO_NUMBER)

    return HttpResponse(str(response.append(dial)), content_type='text/xml')

@csrf_exempt
def save_log_call(request):
    user = request.user
    customer = Customer.objects.get(pk=1)
    if request.method == 'POST':
        duration = request.POST.get('duration', '')
        direction = request.POST.get('direction', '')
        text = 'The ' + direction + ' call lasted ' + duration
        Notification.objects.create(
                    text=text, 
                    customer=customer,
                    date=timezone.now(),
                    channel=Notification.CALL,
                    sent_by=user.name
                )
        return JsonResponse({'message': 'Registro de llamada guardado exitosamente'})
    
    # Manejar otros métodos de solicitud si es necesario
    return JsonResponse({'error': 'Solicitud no válida'}, status=400)
   
@csrf_exempt
def sms_reply(request):
    # Obtén el mensaje entrante y el número de teléfono
    from_number = request.POST.get('From')
    customer = Customer.objects.filter(phone=from_number).first()
    body = request.POST.get('Body')

    notification = Notification(
        text=body, 
        customer=customer,
        date=timezone.now(),
        channel=Notification.REPLY,
        sent_by="Customer Message"
    )
    notification.save()
 
    #response = MessagingResponse()
    #response.message("Gracias por tu mensaje. Pronto te responderemos.")