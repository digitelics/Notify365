from django.shortcuts import render

def login(request):
    return render(request, "security/login_template.html", {})