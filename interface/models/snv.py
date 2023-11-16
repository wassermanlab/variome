from django.db import models
from .variant import Variant


class SNV(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    var_type = models.CharField(max_length=30)
    length = models.IntegerField()
    chr = models.CharField(max_length=3)
    pos = models.IntegerField()
    ref = models.CharField(max_length=255)
    alt = models.CharField(max_length=255)
    cadd_intr = models.CharField(max_length=255, blank=True, null=True)
    cadd_score = models.DecimalField(decimal_places=5, max_digits=10, blank=True, null=True)
    dbsnp_url = models.CharField(max_length=511, blank=True, null=True)
    dbsnp_id = models.CharField(max_length=30, blank=True, null=True)
    ucsc_url = models.CharField(max_length=511, blank=True, null=True)
    ensembl_url = models.CharField(max_length=511, blank=True, null=True)
    clinvar_vcv = models.DecimalField(decimal_places=3, max_digits=15, blank=True, null=True)
    clinvar_url = models.CharField(max_length=511, blank=True, null=True)
    gnomad_url = models.CharField(max_length=511, blank=True, null=True)
    splice_ai = models.DecimalField(decimal_places=5, max_digits=10, blank=True, null=True)

    class Meta:
        db_table = "snvs"

    def __str__(self):
        return self.variant.variant_id