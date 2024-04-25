
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
import os

DOMAIN = os.environ.get('DOMAIN', 'http://localhost:3000')
@login_required
def profile_view(request):
    # do redirect to app
    return redirect(f'{DOMAIN}/')
#    return render(request, 'profile.html', {
#        'user': request.user,
#    })


@login_required
def profile_view_json(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'user':None
        }, status=401)
    user_json = {
        'user':{
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'is_staff': request.user.is_staff,
        'is_active': request.user.is_active,
        'date_joined': request.user.date_joined,
        'last_login': request.user.last_login,
        'csrf_token': get_token(request),
        }
        
    }
    return JsonResponse(user_json, safe=False)
