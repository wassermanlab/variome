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
from django.contrib import admin
from django.urls import path, include
from .library import views as library
from .library_access import views as access
from .views import backend_home_page

api_urls = [
    path('variant/<str:id>', library.variant, name='variant'),
    path('search', library.snv_search, name='search'),
#    path('user/', access.profile_view_json, name='profile'), # REAL AUTH
    path('user/', access.profile_view_stub, name='profile'), # FAKE / DEMO AUTH
]

urlpatterns = [
    path('', backend_home_page, name='backend_home_page'),
    path('admin/', admin.site.urls),
    path('tracking/', include('tracking.urls')),
    path('accounts/profile/', access.profile_view_redirect, name='profile'),
    path('api/', include(api_urls)),
]
