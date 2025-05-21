from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.core.exceptions import ObjectDoesNotExist
import os

from ..models import UserProfile

DOMAIN = os.environ.get("DOMAIN", f"http://localhost:{os.environ.get('FRONTEND_PORT')}")


@login_required
def profile_view_redirect(request):
    # do redirect to app
    return redirect(f"{DOMAIN}/")


#    return render(request, 'profile.html', {
#        'user': request.user,
#    })


def profile_view_stub(request):
    user_json = {
        "user": {
            "username": "demo",
            "email": "demo@example.com",
            "csrf_token": get_token(request),
            "variant_access_count": 10,
            "can_access_variants": True,
        }
    }
    return JsonResponse(user_json, safe=False)


# @login_required
def profile_view_json(request):
    if not request.user.is_authenticated:
        return JsonResponse({"user": None})

    try:
        access_count = request.user.profile.access_count
        can_access_variants = request.user.profile.can_access_variants
    except ObjectDoesNotExist:
        new_profile = UserProfile.objects.create(user=request.user)
        request.user.profile = new_profile
        access_count = new_profile.access_count
        can_access_variants = new_profile.can_access_variants
    user_json = {
        "user": {
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "is_staff": request.user.is_staff,
            "is_active": request.user.is_active,
            "date_joined": request.user.date_joined,
            "last_login": request.user.last_login,
            "variant_access_count": access_count,
            "can_access_variants": can_access_variants,
            "csrf_token": get_token(request),
        }
    }
    return JsonResponse(user_json, safe=False)
