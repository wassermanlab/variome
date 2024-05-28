from django.shortcuts import render

def backend_home_page(request):
    return render(request, 'index.html')