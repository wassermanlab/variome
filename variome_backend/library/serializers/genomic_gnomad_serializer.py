from rest_framework import serializers

from ..models import GenomicGnomadFrequency

from ..serializers import VariantSerializer


class GenomicGnomadFrequencySerializer(serializers.ModelSerializer):
    """ """

    variant = VariantSerializer(read_only=True)

    class Meta:
        model = GenomicGnomadFrequency
        fields = "__all__"
