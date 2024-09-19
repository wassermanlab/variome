from django.db import models
from .variant import Variant


class GenomicGnomadFrequency(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, db_column='variant')
    af_tot = models.DecimalField(decimal_places=10, max_digits=12)
    ac_tot = models.PositiveIntegerField()
    an_tot = models.PositiveIntegerField()
    hom_tot = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = 'Genomic Gnomad Frequencies'

    def __str__(self):
        return self.variant.variant_id