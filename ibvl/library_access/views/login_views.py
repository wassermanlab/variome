
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.urls import reverse
from django.views import View
from django.contrib.auth.views import LoginView
from django.conf import settings


def login(request):
    return render(request, 'login.html')


def login_failed(request):
    return JsonResponse({
        'error': 'Variome Login failed'
    }, status=401)


def logout_view(request):
    logout(request)
    return HttpResponse('Logged out')


class LoginRedirectView(View):

    def get(self, request, *args, **kwargs):
        """redirect Logins to the url set in LOGIN_URL in settings.py"""
        next = request.GET.get(LoginView.redirect_field_name, reverse("/admin"))
        return redirect(reverse(settings.LOGIN_URL) + f"?next={next}")
