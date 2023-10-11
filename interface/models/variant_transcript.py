from django.db import models
from .variant import Variant
from .transcript import Transcript


class VariantTranscript(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE)
    hgvsc = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "variants_transcripts"

    def __str__(self):
        return "_".join([self.variant.variant_id, self.transcript.transcript_id])