from django.db import models
from .variant import Variant


class SNV(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, db_column='variant', related_name='snv')
    type = models.CharField(max_length=30)
    length = models.IntegerField()
    chr = models.CharField(max_length=3)
    pos = models.IntegerField()
    ref = models.CharField(max_length=255)
    alt = models.CharField(max_length=255)
    cadd_intr = models.CharField(max_length=255, blank=True, default="")
    cadd_score = models.DecimalField(decimal_places=5, max_digits=10, null=True)
    dbsnp_url = models.CharField(max_length=511, blank=True, default="")
    dbsnp_id = models.CharField(max_length=30, blank=True, default="")
    ucsc_url = models.CharField(max_length=511, blank=True, default="")
    ensembl_url = models.CharField(max_length=511, blank=True, default="")
    clinvar_vcv = models.DecimalField(decimal_places=3, max_digits=15, null=True)
    clinvar_url = models.CharField(max_length=511, blank=True, default="")
    gnomad_url = models.CharField(max_length=511, blank=True, default="")
    splice_ai = models.DecimalField(decimal_places=5, max_digits=10, null=True)

    class Meta:
        db_table = "snvs"

    def __str__(self):
        return self.variant.variant_id