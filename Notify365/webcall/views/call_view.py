from django.shortcuts import render

from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import jwt

#from dotenv import load_dotenv
import os
import pprint as p

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

