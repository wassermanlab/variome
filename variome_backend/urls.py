"""
URL configuration for variome project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import os
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from .library import views as library
from .library_access import views as access
from .views import backend_home_page, get_site_settings

api_urls = [
    path("variant/<str:id>", library.variant, name="variant"),
    path("search", library.snv_search, name="search"),
    path("user/", access.profile_view_json, name="profile"),
    path("settings", get_site_settings, name="settings"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tracking/", access.tracking_dashboard, name="tracking_dashboard"),
    path("accounts/profile/", access.profile_view_redirect, name="profile"),
    path("api/", include(api_urls)),
]


def redirect_to_login(request):
    response = redirect("accounts/login/")
    return response


# brad: this is better handling of redirect IMO, but leaving commented out so as to avoid unexpected confusion
#    if request.user.is_authenticated and request.user.is_staff:
#        response = redirect('backend/admin')
#    else:
#        response = redirect('accounts/login/')
#    return response


if os.getenv("AUTH_AZUREAD", "False").lower() == "true":
    urlpatterns.extend(
        [
            path("", redirect_to_login, name="redirect_to_login"),
            path("accounts/login/", access.LoginRedirectView.as_view(), name="login"),
            path("accounts/logout", access.logout_view, name="logout"),
            path("oauth2/", include("django_auth_adfs.urls")),
        ]
    )
else:
    urlpatterns.extend(
        [
            path("", backend_home_page, name="backend_home_page"),
            path("accounts/login/", access.admin_login, name="login"),
            path("accounts/logout", access.logout_view, name="logout"),
        ]
    )
