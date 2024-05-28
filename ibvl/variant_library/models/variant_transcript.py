from django.db import models
from .variant import Variant
from .transcript import Transcript


class VariantTranscript(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, db_column='variant')
    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE, db_column='transcript')
    hgvsc = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        db_table = "variants_transcripts"
        verbose_name_plural = 'Variant Transcripts'

    def __str__(self):
        return "_".join([self.variant.variant_id, self.transcript.transcript_id])