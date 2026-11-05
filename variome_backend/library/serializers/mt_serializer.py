from rest_framework import serializers

from ..models import MT
from .variant_serializer import VariantSerializer


class MTSerializer(serializers.ModelSerializer):
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = MT
        fields = "__all__"
