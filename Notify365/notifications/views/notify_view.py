from django.shortcuts import render

# Create your views here.

def notify(request):
    return render(request, 'notifications/notify_template.html', {})

def sms(request):
    return render(request, 'notifications/text_message_template.html', {})



