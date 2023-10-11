from django.db import models
from .variant import Variant


class GenomicIBVLFrequency(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    af_tot = models.DecimalField(decimal_places=10, max_digits=12)
    af_xy = models.DecimalField(decimal_places=10, max_digits=12)
    af_xx = models.DecimalField(decimal_places=10, max_digits=12)
    ac_tot = models.DecimalField(decimal_places=3, max_digits=12)
    ac_xy = models.DecimalField(decimal_places=3, max_digits=12)
    ac_xx = models.DecimalField(decimal_places=3, max_digits=12)
    an_tot = models.DecimalField(decimal_places=3, max_digits=12)
    an_xy = models.DecimalField(decimal_places=3, max_digits=12)
    an_xx = models.DecimalField(decimal_places=3, max_digits=12)
    hom_tot = models.DecimalField(decimal_places=3, max_digits=12)
    hom_xy = models.DecimalField(decimal_places=3, max_digits=12)
    hom_xx = models.DecimalField(decimal_places=3, max_digits=12)
    quality = models.DecimalField(decimal_places=3, max_digits=12)

    class Meta:
        db_table = "genomic_ibvl_frequencies"

    def __str__(self):
        return self.variant.variant_id