from rest_framework import serializers

from ..models import (
    VariantAnnotation
)

from ..serializers import (
    VariantTranscriptSerializer,
)


class VariantAnnotationSerializer(serializers.ModelSerializer):
    """
    """

    class Meta:
        model = VariantAnnotation
        fields = [
            "id", "hgvsp", "polyphen", "sift"
        ]