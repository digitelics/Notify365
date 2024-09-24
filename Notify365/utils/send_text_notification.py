from twilio.rest import Client

TWIML_APP_SID = "AP6bb2acda7405e3e3f0fd41a80f70f116"
TWILIO_ACCOUNT_SID = "ACa5f0c87dab3e0a1abb35c335dce1ec27"
TWILIO_AUTH_TOKEN = "70225e2a1d06e7d42d7849ec78b56a32"
TWILIO_API_KEY_SID = "SK36f670a4fb369a1a497b00f39b23bc0c"
TWILIO_API_KEY_SECRET = "nB1jsV3JBzYSFLb1hxgIv2xlw4zt08fC"
TWILIO_NUMBER = "+18448689065"

def send_sms(to, message, media_urls=None):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    print('parametro: '+ str(TWILIO_ACCOUNT_SID))
    try:
        message_params = {
            'body': message,
            'from_': TWILIO_NUMBER,
            'to': to
        }
        if media_urls:
            print(media_urls)
            message_params['media_url'] = media_urls
        
        message = client.messages.create(**message_params)
        return message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return "Error"
