from django.db import models
from .variant import Variant


class GenomicGnomadFrequency(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, db_column='variant')
    af_tot = models.DecimalField(decimal_places=10, max_digits=12)
    af_popmax = models.DecimalField(decimal_places=10, max_digits=12, null=True)
    ac_tot = models.DecimalField(decimal_places=3, max_digits=12)
    an_tot = models.DecimalField(decimal_places=3, max_digits=12)
    hom_tot = models.DecimalField(decimal_places=3, max_digits=12)

    class Meta:
        verbose_name_plural = 'Genomic Gnomad Frequencies'

    def __str__(self):
        return self.variant.variant_id