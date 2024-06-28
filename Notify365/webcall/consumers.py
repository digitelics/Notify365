'''import json
from channels.generic.websocket import WebsocketConsumer

class MyConsumer(WebsocketConsumer):
    def connect(self):
        # Lógica de conexión inicial
        print('Conexion establecida')
        self.accept()


    def disconnect(self, close_code):
        # Lógica de desconexión
        print('se ha desconectado')
        pass

    def receive(self, text_data):
        # Lógica de recepción de mensajes
        print('mensaje recibido')
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.send(text_data=json.dumps({
            'message':message
        }))
'''