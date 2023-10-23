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

    class Meta:
        model = VariantAnnotation
        fields = [
            "id", "hgvsp", "polyphen", "sift"
        ]