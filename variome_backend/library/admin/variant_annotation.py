from django.contrib import admin
from ..models import VariantAnnotation
from variome_backend.admin_components.filters import InputFilter


class VariantIdFilter(InputFilter):
    parameter_name = "variant_id"
    title = "Variant ID"

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(
                variant_transcript__variant__variant_id__icontains=self.value()
            )
        return queryset


class VariantAnnotationAdmin(admin.ModelAdmin):
    list_display = ("id", "variant_transcript", "hgvsp", "polyphen", "sift")
    list_display_links = ("id", "variant_transcript")
    list_filter = (VariantIdFilter,)
    autocomplete_fields = ("variant_transcript",)


admin.site.register(VariantAnnotation, VariantAnnotationAdmin)
