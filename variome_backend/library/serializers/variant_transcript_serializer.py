from rest_framework import serializers

from ..models import (
    VariantTranscript
)

from ..serializers import (
    TranscriptSerializer,
    VariantSerializer
)


class VariantTranscriptSerializer(serializers.ModelSerializer):
    """
    """
    variant = VariantSerializer(read_only=True)
    transcript = TranscriptSerializer(read_only=True)

    class Meta:
        model = VariantTranscript
        fields = [
            "id", "variant", "transcript", "hgvsc"
        ]