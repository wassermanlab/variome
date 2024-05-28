from django.apps import AppConfig
from django.apps import AppConfig
import os

absolute_dir = os.path.dirname(os.path.abspath(__file__))

class AccessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ibvl.variant_library_access'
    verbose_name = 'Variant Library Access'
#    path = app_dir = os.path.join(absolute_dir, 'variant_library_access')
    

class IbvlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ibvl'
    verbose_name = 'Variant Library'
