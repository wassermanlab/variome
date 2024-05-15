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
from . import views

api_urls = [
    path('snv/<str:variant_id>', views.snv_metadata, name='snv_metadata'),
    path('annotations/<str:variant_id>', views.snv_annotations, name='snv_annotations'),
    path('genomic_population_frequencies/<str:variant_id>', views.genomic_population_frequencies, name='genomic_population_frequencies'),
    path('search', views.snv_search, name='search'),
    path('csrf/', views.get_csrf, name='api-csrf'),
    path('login/', views.login_view, name='api-login'),
    path('logout/', views.logout_view, name='api-logout'),
    path('session/', views.session_view, name='api-session'),
    path('whoami/', views.whoami_view, name='api-whoami'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('api/user/', views.profile_view_json, name='profile'),
    path('tracking/', include('tracking.urls')),
]
