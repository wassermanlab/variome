from django.contrib import admin
from interface.models import SNV


class SNVAdmin(admin.ModelAdmin):


    list_display = ('id', 'variant', 'var_type')
    list_display_links = ('id', 'variant')
    #list_filter = (IdFilter,)

admin.site.register(SNV, SNVAdmin)