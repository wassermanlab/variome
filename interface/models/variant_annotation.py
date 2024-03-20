from django.db import models
from .variant_transcript import VariantTranscript

IMPACT_CHOICES = [
    ('HIGH','High'),
    ('MODERATE','Moderate'),
    ('LOW','Low'),
    ('MODIFIER','Modifier'),
    ('','(unknown)'),
]

class VariantAnnotation(models.Model):
    variant_transcript = models.ForeignKey(VariantTranscript, on_delete=models.CASCADE, db_column='variant_transcript')
    hgvsp = models.CharField(max_length=255, blank=True)
    polyphen = models.CharField(max_length=255, blank=True)
    sift = models.CharField(max_length=255, blank=True)
    impact = models.CharField(max_length=20, blank=True, default='', choices=IMPACT_CHOICES)

    class Meta:
        db_table = "variants_annotations"
        verbose_name_plural = 'Variant Annotations'

    #def __str__(self):
    #    return "_".join([self.variant.variant_id, self.transcript.transcript_id])