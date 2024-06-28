from django.shortcuts import render

def client(request):
    
    mensaje = "Hola mundo mundial!"
    categories = ['fotos', 'news', 'services', 'blog']
    context = {'mensaje' : mensaje, 'categories': categories}
    return render(request, 'customers/client_template.html', context)

