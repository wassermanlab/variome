from rest_framework import serializers

from bvl.models import (
    VariantAnnotation
)

from bvl.serializers import (
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