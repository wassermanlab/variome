from django.db import models
from .variant_transcript import VariantTranscript


class VariantAnnotation(models.Model):
    variant_transcript = models.ForeignKey(VariantTranscript, on_delete=models.CASCADE)
    hgvsp = models.CharField(max_length=255, blank=True, null=True)
    polyphen = models.CharField(max_length=255, blank=True, null=True)
    sift = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "variants_annotations"

    #def __str__(self):
    #    return "_".join([self.variant.variant_id, self.transcript.transcript_id])