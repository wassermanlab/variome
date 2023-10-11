from rest_framework import serializers

from interface.models import (
    GenomicIBVLFrequency
)

from interface.serializers import (
    VariantSerializer
)


class GenomicIBVLFrequencySerializer(serializers.ModelSerializer):
    """
    """
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = GenomicIBVLFrequency
        fields = "__all__"