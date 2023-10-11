from rest_framework import serializers

from interface.models import (
    VariantAnnotation
)

from interface.serializers import (
    VariantTranscriptSerializer,
)


class VariantAnnotationSerializer(serializers.ModelSerializer):
    """
    """
    variant_transcript = VariantTranscriptSerializer(read_only=True)

    class Meta:
        model = VariantAnnotation
        fields = [
            "id", "variant_transcript", "hgvsp", "polyphen", "sift"
        ]