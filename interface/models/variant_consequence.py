from django.db import models
from .variant_transcript import VariantTranscript
from .severity import Severity


class VariantConsequence(models.Model):
    variant_transcript = models.ForeignKey(VariantTranscript, on_delete=models.CASCADE)
    severity = models.ForeignKey(Severity, on_delete=models.CASCADE)

    class Meta:
        db_table = "variants_consequences"

    #def __str__(self):
    #    return "_".join([self.variant.variant_id, self.transcript.transcript_id])