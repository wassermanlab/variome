from rest_framework import serializers

from ibvl.models import (
    GenomicGnomadFrequency
)

from ibvl.serializers import (
    VariantSerializer
)


class GenomicGnomadFrequencySerializer(serializers.ModelSerializer):
    """
    """
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = GenomicGnomadFrequency
        fields = "__all__"