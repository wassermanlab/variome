from rest_framework import serializers

from bvl.models import (
    GenomicGnomadFrequency
)

from bvl.serializers import (
    VariantSerializer
)


class GenomicGnomadFrequencySerializer(serializers.ModelSerializer):
    """
    """
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = GenomicGnomadFrequency
        fields = "__all__"