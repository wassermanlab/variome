from django.contrib import admin
from ..models import Gene


class GeneAdmin(admin.ModelAdmin):


    list_display = ('id', 'short_name')
    list_display_links = ('id', 'short_name')
    #list_filter = (IdFilter,)

admin.site.register(Gene, GeneAdmin)