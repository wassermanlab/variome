from django.contrib import admin
from bvl.models import Severity


class SeverityAdmin(admin.ModelAdmin):


    list_display = ('id', 'severity_number', 'consequence')
    list_display_links = ('id', 'severity_number')
    #list_filter = (IdFilter,)

admin.site.register(Severity, SeverityAdmin)