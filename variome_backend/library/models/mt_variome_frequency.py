from django.db import models

from .variant import Variant


class MtVariomeFrequency(models.Model):
    variant = models.OneToOneField(
        Variant, on_delete=models.CASCADE, db_column="variant"
    )
    an = models.PositiveIntegerField(null=True, blank=True)
    ac_hom = models.PositiveIntegerField(null=True, blank=True)
    ac_het = models.PositiveIntegerField(null=True, blank=True)
    af_hom = models.DecimalField(
        decimal_places=10, max_digits=12, null=True, blank=True
    )
    af_het = models.DecimalField(
        decimal_places=10, max_digits=12, null=True, blank=True
    )
    max_hl = models.DecimalField(
        decimal_places=10, max_digits=12, null=True, blank=True
    )
    hl_hist = models.TextField(blank=True, default="")

    class Meta:
        verbose_name_plural = "Mitochondrial Variome frequencies"

    def __str__(self):
        return self.variant.variant_id
