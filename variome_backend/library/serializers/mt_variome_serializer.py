from rest_framework import serializers

from ..models import MtVariomeFrequency
from .variant_serializer import VariantSerializer


class MtVariomeFrequencySerializer(serializers.ModelSerializer):
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = MtVariomeFrequency
        fields = "__all__"
