from rest_framework import serializers

from bvl.models import (
    Transcript
)

from bvl.serializers import (
    GeneSerializer
)

class TranscriptSerializer(serializers.ModelSerializer):
    """
    """
    gene = GeneSerializer(read_only=True)

    class Meta:
        model = Transcript
        fields = [
            "id", "transcript_id", "gene", "transcript_type", "tsl"
        ]