from rest_framework import serializers

from bvl.models import (
    VariantConsequence
)

from bvl.serializers import (
    VariantTranscriptSerializer,
    SeveritySerializer
)


class VariantConsequenceSerializer(serializers.ModelSerializer):
    """
    """
    variant_transcript = VariantTranscriptSerializer(read_only=True)
    severity = SeveritySerializer(read_only=True)

    class Meta:
        model = VariantConsequence
        fields = [
            "id", "variant_transcript", "severity"
        ]