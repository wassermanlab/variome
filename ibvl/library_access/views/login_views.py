
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.urls import reverse
from django.views import View
from django.conf import settings

# unused? verify
def login(request):
    return render(request, 'login.html')

# for development
def admin_login(request):
    return redirect('/admin/login')


def login_failed(request):
    return JsonResponse({
        'error': 'Variome Login failed'
    }, status=401)


def logout_view(request):
    logout(request)
    return HttpResponse(f'Logged out <br/><br/><a href="{settings.SITE_URL}">Back to Home</a>')


class LoginRedirectView(View):

    def get(self, request, *args, **kwargs):
        """redirect Logins to the url set in LOGIN_URL in settings.py"""
        next = request.headers["referer"]
        return redirect(reverse(settings.LOGIN_URL) + f"?next={next}")
