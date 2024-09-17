from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.conf import settings

def backend_home_page(request):
    # if production ...?
    # if developemnt: (case handled in urls.py)
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