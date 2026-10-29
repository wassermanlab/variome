from rest_framework import serializers

from ..models import MtGnomadFrequency
from .variant_serializer import VariantSerializer


class MtGnomadFrequencySerializer(serializers.ModelSerializer):
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = MtGnomadFrequency
        fields = "__all__"
