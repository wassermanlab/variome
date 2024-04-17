from django.contrib import admin
from ibvl.models import Variant
from .components.filters import InputFilter

class VariantIdFilter(InputFilter):
    parameter_name = 'variant_id'
    title = 'Variant ID'

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(variant_id__icontains=self.value())
        return queryset

class VariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'variant_id', 'var_type')
    list_display_links = ('id', 'variant_id')
    list_filter = (VariantIdFilter, 'var_type')

admin.site.register(Variant, VariantAdmin)