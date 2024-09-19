from django.db import models
from .variant import Variant


class GenomicVariomeFrequency(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, db_column='variant')
    af_tot = models.DecimalField(decimal_places=10, max_digits=12)
    ac_tot = models.PositiveIntegerField()
    an_tot = models.PositiveIntegerField()
    hom_tot = models.PositiveIntegerField()
    hom_xy = models.PositiveIntegerField()
    hom_xx = models.PositiveIntegerField()
    quality = models.IntegerField()

    class Meta:
        verbose_name_plural = 'Genomic Variome Frequencies'

    def __str__(self):
        return self.variant.variant_id