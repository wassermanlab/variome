from django.contrib import admin

from ..models import MT, MtGnomadFrequency, MtVariomeFrequency


@admin.register(MT)
class MTAdmin(admin.ModelAdmin):
    list_display = ("id", "variant", "pos", "ref", "alt", "dbsnp_id", "clinvar_vcv")
    search_fields = ("variant__variant_id", "dbsnp_id")
    autocomplete_fields = ("variant",)


@admin.register(MtVariomeFrequency)
class MtVariomeFrequencyAdmin(admin.ModelAdmin):
    list_display = (
        "id", "variant", "an", "ac_hom", "ac_het", "af_hom", "af_het", "max_hl"
    )
    search_fields = ("variant__variant_id",)
    autocomplete_fields = ("variant",)


@admin.register(MtGnomadFrequency)
class MtGnomadFrequencyAdmin(admin.ModelAdmin):
    list_display = (
        "id", "variant", "an", "ac_hom", "ac_het", "af_hom", "af_het", "max_hl"
    )
    search_fields = ("variant__variant_id",)
    autocomplete_fields = ("variant",)
