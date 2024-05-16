from rest_framework import serializers

from ibvl.models import (
    VariantAnnotation
)

from ibvl.serializers import (
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