from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .library.models import Variant
from variome_backend.models import VariomeSettings
from django.contrib.auth.decorators import login_required

def backend_home_page(request):
    # if production ...?
    # if development: (case handled in urls.py)
    return login_view(request)

# for development environment. logs in a non-staff, non-superadmin user
# note: login via django admin dashboard is sufficient for most dev purposes
# this login flow is only needed for testing non-admin user auth behaviour
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect(settings.SITE_URL)  # replace 'home' with your target page
            else:
                messages.info(request, "Invalid username or password.")
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request, 'development-mode-login.html', context={'form': form})

#@login_required
def get_site_settings(request):
    site_settings = VariomeSettings.objects.get(pk=1)
    example_variant = site_settings.example_snv
        
    settings = {"settings": {"site_title": site_settings.site_title, "home_page_message": site_settings.home_page_message}}
    
    if isinstance(example_variant, Variant) & request.user.is_authenticated:    
        settings["settings"]["example_snv"] = {"id": example_variant.id, "var_id": example_variant.variant_id}
    else:
        settings["settings"]["example_snv"] = None
    
    return JsonResponse(settings)