from django.db import models
from .variant_transcript import VariantTranscript

IMPACT_CHOICES = [
    ("HIGH", "High"),
    ("MODERATE", "Moderate"),
    ("LOW", "Low"),
    ("MODIFIER", "Modifier"),
    ("", "(unknown)"),
]


class VariantAnnotation(models.Model):
    variant_transcript = models.ForeignKey(
        VariantTranscript,
        on_delete=models.CASCADE,
        db_column="variant_transcript",
        related_name="annotation",
    )
    hgvsp = models.CharField(max_length=255, blank=True, default="")
    polyphen = models.CharField(max_length=255, blank=True, default="")
    sift = models.CharField(max_length=255, blank=True, default="")
    impact = models.CharField(
        max_length=20, blank=True, default="", choices=IMPACT_CHOICES
    )

    class Meta:
        verbose_name_plural = "Variant Annotations"

    # def __str__(self):
    #    return "_".join([self.variant.variant_id, self.transcript.transcript_id])
