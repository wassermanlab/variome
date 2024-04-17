from django.contrib import admin
from bvl.models import VariantTranscript


class VariantTranscriptAdmin(admin.ModelAdmin):


    list_display = ('id', 'variant', 'transcript', 'hgvsc')
    list_display_links = ('id', 'variant', 'transcript')
    #list_filter = (IdFilter,)

admin.site.register(VariantTranscript, VariantTranscriptAdmin)