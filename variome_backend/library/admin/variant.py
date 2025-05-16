from django.contrib import admin
from ..models import Variant
from variome_backend.admin_components.filters import InputFilter

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
    search_fields = ('variant_id',)

admin.site.register(Variant, VariantAdmin)