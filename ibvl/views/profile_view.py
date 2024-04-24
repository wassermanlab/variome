
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    request.foo = "bear"
    is_json = request.GET.get('json', False)
    if is_json:
        return profile_view_json(request)
    else:
        return render(request, 'profile.html', {
            'user': request.user,
    #        'profile': request.user.profile
        })


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
        'last_login': request.user.last_login
        }
        
    }
    return JsonResponse(user_json, safe=False)
