from django.contrib import admin
from interface.models import Variant


class VariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'variant_id', 'var_type')
    list_display_links = ('id', 'variant_id')
    #list_filter = (IdFilter,)

admin.site.register(Variant, VariantAdmin)