from django.contrib import admin
from interface.models import VariantAnnotation


class VariantAnnotationAdmin(admin.ModelAdmin):


    list_display = ('id', 'variant_transcript', 'hgvsp', 'polyphen', 'sift')
    list_display_links = ('id', 'variant_transcript')
    #list_filter = (IdFilter,)

admin.site.register(VariantAnnotation, VariantAnnotationAdmin)