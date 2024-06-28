
'''import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import webcall.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notify365.settings')

application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'websocket':AuthMiddlewareStack(
        URLRouter(webcall.routing.websolcket_urlpatterns)
    ),
})
'''
