from django.contrib import admin
from ..models import Transcript


class TranscriptAdmin(admin.ModelAdmin):


    list_display = ('id', 'transcript_id', 'transcript_type', 'gene')
    list_display_links = ('id', 'transcript_id')
    
    autocomplete_fields = ('gene',)
    search_fields = ('transcript_id',)
    #list_filter = (IdFilter,)

admin.site.register(Transcript, TranscriptAdmin)