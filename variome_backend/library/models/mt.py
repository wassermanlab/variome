from django.db import models

from .variant import Variant


class MT(models.Model):
    variant = models.OneToOneField(
        Variant, on_delete=models.CASCADE, db_column="variant", related_name="mt"
    )
    pos = models.IntegerField(db_index=True)
    ref = models.CharField(max_length=400)
    alt = models.CharField(max_length=255)
    ucsc_url = models.CharField(max_length=511, blank=True, default="")
    mitomap_url = models.CharField(max_length=511, blank=True, default="")
    gnomad_url = models.CharField(max_length=511, blank=True, default="")
    dbsnp_id = models.CharField(max_length=30, blank=True, default="", db_index=True)
    dbsnp_url = models.CharField(max_length=511, blank=True, default="")
    clinvar_url = models.CharField(max_length=511, blank=True, default="")
    clinvar_vcv = models.DecimalField(
        decimal_places=3, max_digits=15, blank=True, null=True, db_index=True
    )

    class Meta:
        verbose_name_plural = "Mitochondrial variants"

    def __str__(self):
        return self.variant.variant_id
