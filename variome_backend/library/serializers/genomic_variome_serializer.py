from rest_framework import serializers

from ..models import (
    GenomicVariomeFrequency
)

from ..serializers import (
    VariantSerializer
)


class GenomicVariomeFrequencySerializer(serializers.ModelSerializer):
    """
    """
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = GenomicVariomeFrequency
        fields = "__all__"