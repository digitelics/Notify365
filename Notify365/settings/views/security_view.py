from django.shortcuts import render

# Create your views here.
def security(request):
    return render(request, "settings/security_template.html", {})