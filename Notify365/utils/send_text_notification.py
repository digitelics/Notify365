from twilio.rest import Client
import os
from django.conf import settings

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')

def send_sms(to, message, media_urls=None):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        message_params = {
            'body': message,
            'from_': TWILIO_NUMBER,
            'to': to
        }
        if media_urls:
            url = settings.BASE_URL + settings.STATIC_URL + "files/notification_attach" + media_urls 
            print(url)
            message_params['media_url'] = url
        
        message = client.messages.create(**message_params)
        return message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None
