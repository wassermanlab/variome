# admin.py

from django.contrib import admin
from django.conf import settings

admin.site.site_url = settings.SITE_URL

from django.contrib import admin
""" 
class VariomeAdminSite(admin.AdminSite):
    site_header = 'My administration'
    site_title = 'My site admin'

    def get_app_list(self, request):
        ordering = {
            "libray_access": 1,
            "library": 2,
            "tracking": 3,
            "pghistory": 4
        }
        app_dict = self._build_app_dict(request)
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the apps according to the ordering.
        app_list.sort(key=lambda x: ordering.get(x['app_label'], 6))

        return app_list

admin_site = VariomeAdminSite(name='variome_admin_site') """