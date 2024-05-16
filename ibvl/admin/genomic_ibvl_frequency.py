from django.contrib import admin
from ibvl.models import GenomicIBVLFrequency


class GenomicIBVLFrequencyAdmin(admin.ModelAdmin):


    list_display = ('id', 'variant', 'af_tot', 'ac_tot', 'an_tot', 'hom_tot', 'quality')
    list_display_links = ('id', 'variant')
    #list_filter = (IdFilter,)

admin.site.register(GenomicIBVLFrequency, GenomicIBVLFrequencyAdmin)