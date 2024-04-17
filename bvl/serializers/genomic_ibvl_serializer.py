from rest_framework import serializers

from bvl.models import (
    GenomicIBVLFrequency
)

from bvl.serializers import (
    VariantSerializer
)


class GenomicIBVLFrequencySerializer(serializers.ModelSerializer):
    """
    """
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = GenomicIBVLFrequency
        fields = "__all__"