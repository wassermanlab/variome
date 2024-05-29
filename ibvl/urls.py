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
#    path('snv/<str:variant_id>', bvl.snv_metadata, name='snv_metadata'),
#    path('annotations/<str:variant_id>', bvl.snv_annotations, name='snv_annotations'),
#    path('genomic_population_frequencies/<str:variant_id>', bvl.genomic_population_frequencies, name='genomic_population_frequencies'),
    path('search', library.snv_search, name='search'),
    path('user/', access.profile_view_json, name='profile'),
#    path('csrf/', views.get_csrf, name='api-csrf'),
#    path('login/', views.login_view, name='api-login'),
#    path('logout/', views.logout_view, name='api-logout'),
#    path('session/', views.session_view, name='api-session'),
#    path('whoami/', views.whoami_view, name='api-whoami'),
]

urlpatterns = [
    path('', backend_home_page, name='backend_home_page'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('tracking/', include('tracking.urls')),
    path('accounts/profile/', access.profile_view_redirect, name='profile'),
    path('api/', include(api_urls)),
]
