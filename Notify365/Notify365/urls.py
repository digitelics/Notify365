
from django.contrib import admin
from django.urls import path
from .views import client_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('client/', client_view.client, name="client"),
]
