from django.db import models
from .variant import Variant


class GenomicVariomeFrequency(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, db_column='variant')
    af_tot = models.DecimalField(decimal_places=10, max_digits=12, null=True)
    af_xx = models.DecimalField(decimal_places=10, max_digits=12, null=True)
    af_xy = models.DecimalField(decimal_places=10, max_digits=12, null=True)
    ac_tot = models.PositiveIntegerField(null=True)
    an_tot = models.PositiveIntegerField()
    ac_xx = models.PositiveIntegerField(null=True)
    ac_xy = models.PositiveIntegerField(null=True)
    an_xx = models.PositiveIntegerField(null=True)
    an_xy = models.PositiveIntegerField(null=True)
    hom_tot = models.PositiveIntegerField(null=True)
    hom_xy = models.PositiveIntegerField(null=True)
    hom_xx = models.PositiveIntegerField(null=True)
    quality = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = 'Genomic Variome Frequencies'

    def __str__(self):
        return self.variant.variant_id