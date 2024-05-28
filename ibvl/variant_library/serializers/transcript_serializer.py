from rest_framework import serializers

from ..models import (
    Transcript
)

from ..serializers import (
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