
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('client/', views.client_view.client, name="client"),
    path('', views.index, name="dashboard"),
    path('test/', views.test, name='test'),
    path('login/', views.login_view.login, name="login"),
    path('registration/', views.registration_view.registration, name="registration"),
]
