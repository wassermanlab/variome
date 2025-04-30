from django.contrib import admin
from ..models import VariantConsequence
from ibvl.admin_components.filters import InputFilter

class VariantIdFilter(InputFilter):
    parameter_name = 'variant_id'
    title = 'Variant ID'

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(variant_transcript__variant__variant_id__icontains=self.value())
        return queryset

class VariantConsequenceAdmin(admin.ModelAdmin):


    list_display = ('id', 'variant_transcript', 'severity')
    list_display_links = ('id', 'variant_transcript')
    list_filter = (VariantIdFilter,)
    autocomplete_fields = ('variant_transcript',)

admin.site.register(VariantConsequence, VariantConsequenceAdmin)