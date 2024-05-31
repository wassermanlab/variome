
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render



def login(request):
    return render(request, 'login.html')
    
    
def login_failed(request):
    return JsonResponse({
        'error': 'Variome Login failed'
    }, status=401)