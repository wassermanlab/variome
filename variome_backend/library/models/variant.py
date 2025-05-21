from django.db import models


VAR_CHOICES = [("SNV", "SNV"), ("M", "Mitochondrial"), ("SV", "SV"), ("INDEL", "INDEL")]


class Variant(models.Model):
    variant_id = models.CharField(max_length=355, unique=True)
    var_type = models.CharField(max_length=30, choices=VAR_CHOICES)
    filter = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        verbose_name_plural = "Variants"

    def __str__(self):
        return self.variant_id
