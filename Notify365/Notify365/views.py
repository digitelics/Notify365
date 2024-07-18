from django.shortcuts import render

# Create your views here.
from customers.views import client_view, customer_view, customer_service_view, note_view, document_view, contact_view
from security.views import login_view, registration_view, user_view, account_view
from settings.views import setting_view, company_view, security_view, notification_view, general_view, product_view
from notifications.views import notify_view
from schedules.views import calendar_views
from webcall.views import call_view


from django.contrib.auth.decorators import login_required

@login_required
def index (request):
     return render(request, 'index.html')

def test (request):
     
     return render(request, 'test.html', {})


