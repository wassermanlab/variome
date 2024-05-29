from django.contrib import admin
from ..models import VariantConsequence


class VariantConsequenceAdmin(admin.ModelAdmin):


    list_display = ('id', 'variant_transcript', 'severity')
    list_display_links = ('id', 'variant_transcript')
    #list_filter = (IdFilter,)

admin.site.register(VariantConsequence, VariantConsequenceAdmin)