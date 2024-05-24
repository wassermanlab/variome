from rest_framework import serializers

from ibvl.models import (
    GenomicVariomeFrequency
)

from ibvl.serializers import (
    VariantSerializer
)


class GenomicVariomeFrequencySerializer(serializers.ModelSerializer):
    """
    """
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = GenomicVariomeFrequency
        fields = "__all__"