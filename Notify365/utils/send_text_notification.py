from twilio.rest import Client

TWIML_APP_SID = "AP6bb2acda7405e3e3f0fd41a80f70f116"
TWILIO_ACCOUNT_SID = "ACa5f0c87dab3e0a1abb35c335dce1ec27"
TWILIO_AUTH_TOKEN = "70225e2a1d06e7d42d7849ec78b56a32"
TWILIO_API_KEY_SID = "SK36f670a4fb369a1a497b00f39b23bc0c"
TWILIO_API_KEY_SECRET = "nB1jsV3JBzYSFLb1hxgIv2xlw4zt08fC"
TWILIO_NUMBER = "+18448689065"
from twilio.base.exceptions import TwilioRestException


def send_sms(to, message, media_urls=None):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    print('parametro: '+ str(TWILIO_ACCOUNT_SID))
    try:
        if not to or not message:
            print("Error: El número de teléfono y el mensaje son obligatorios.")
            return "Error: Missing required parameters"
        
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
    except TwilioRestException as e:
        print(f"Twilio error al enviar el SMS: {e}")
        return "Twilio Error"
    except Exception as e:
        print(f"Error enviando SMS: {e}")
        return "Error"


def validate_gsm7(text):
    # Lista de caracteres GSM-7 permitidos
    gsm7_characters = (
        '@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !"#¤%&\'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà'
    )

    # Lista para almacenar los caracteres no válidos
    invalid_characters = []

    # Verificar cada carácter en el texto
    for char in text:
        if char not in gsm7_characters:
            invalid_characters.append(char)

    if invalid_characters:
        return {
            "is_valid": False,
            "message": f"El texto contiene caracteres no compatibles con GSM-7: {', '.join(set(invalid_characters))}",
            "invalid_characters": list(set(invalid_characters))
        }
    else:
        return {
            "is_valid": True,
            "message": "El texto cumple con el estándar GSM-7.",
            "invalid_characters": []
        }