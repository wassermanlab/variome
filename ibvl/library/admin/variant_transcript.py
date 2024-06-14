from django.contrib import admin
from ..models import VariantTranscript


class VariantTranscriptAdmin(admin.ModelAdmin):


    list_display = ('id', 'variant', 'transcript', 'hgvsc')
    list_display_links = ('id', 'variant', 'transcript')
    
    search_fields = ('variant__variant_id', 'transcript__transcript_id')
    
    autocomplete_fields = ('variant', 'transcript')
    #list_filter = (IdFilter,)

admin.site.register(VariantTranscript, VariantTranscriptAdmin)