from django.contrib import admin
from ..models import SNV

from variome_backend.admin_components.filters import InputFilter

class VariantIdFilter(InputFilter):
    parameter_name = 'variant_id'
    title = 'Variant ID'

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(variant__variant_id__icontains=self.value())
        return queryset

class SNVAdmin(admin.ModelAdmin):


    list_display = ('id', 'variant', 'type', 'length', 'chr', 'pos', 'ref', 'alt', 'cadd_intr', 'cadd_score', 'dbsnp_url', 'dbsnp_id', 'ucsc_url', 'ensembl_url', 'clinvar_vcv', 'clinvar_url', 'gnomad_url', 'splice_ai')
    list_display_links = ('id', 'variant')
    list_filter = (VariantIdFilter,)
    autocomplete_fields = ('variant',)

admin.site.register(SNV, SNVAdmin)
