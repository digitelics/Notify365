from django.shortcuts import render

# Create your views here.
from customers.views import client_view
from security.views import login_view, registration_view

def index (request):
     return render(request, 'index.html', {})

def test (request):
     return render(request, 'test.html', {})

