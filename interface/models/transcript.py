from django.db import models
from .gene import Gene

# TODO: Add transcript choices here
TRANSCRIPT_CHOICES = []


class Transcript(models.Model):
    transcript_id = models.CharField(max_length=100, unique=True)
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)
    # TODO: Add choices for transcript type
    transcript_type = models.CharField(max_length=1)
    tsl = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "transcripts"

    def __str__(self):
        return self.transcript_id