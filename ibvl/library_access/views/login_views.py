
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth import logout


def login(request):
    return render(request, 'login.html')
    
    
def login_failed(request):
    return JsonResponse({
        'error': 'Variome Login failed'
    }, status=401)
    
def logout_view(request):
    logout(request)
    return HttpResponse('Logged out')