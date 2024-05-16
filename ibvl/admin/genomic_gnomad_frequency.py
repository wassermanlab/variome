from django.contrib import admin
from ibvl.models import GenomicGnomadFrequency


class GenomicGnomadFrequencyAdmin(admin.ModelAdmin):

    list_display = ('id', 'variant', 'af_tot', 'ac_tot', 'an_tot', 'hom_tot')
    list_display_links = ('id', 'variant')
    #list_filter = (IdFilter,)

admin.site.register(GenomicGnomadFrequency, GenomicGnomadFrequencyAdmin)