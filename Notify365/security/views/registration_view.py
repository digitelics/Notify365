from django.shortcuts import render

def registration(request):
    return render(request, "security/register_template.html", {})