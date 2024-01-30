from django.db import models


VAR_CHOICES = [
    ("SNV", "SNV"),
    ("M", "Mitochondrial"),
    ("SV", "SV")
]


class Variant(models.Model):
    variant_id = models.CharField(max_length=255, unique=True)
    var_type = models.CharField(max_length=30, choices=VAR_CHOICES)
    filter = models.CharField(max_length=100)

    class Meta:
        db_table = "variants"

    def __str__(self):
        return self.variant_id