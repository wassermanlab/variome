from rest_framework import serializers

from ibvl.models import (
    GenomicIBVLFrequency
)

from ibvl.serializers import (
    VariantSerializer
)


class GenomicIBVLFrequencySerializer(serializers.ModelSerializer):
    """
    """
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = GenomicIBVLFrequency
        fields = "__all__"