from rest_framework import serializers

from ..models import (
    Variant
)

class VariantSerializer(serializers.ModelSerializer):
    """
    """
    class Meta:
        model = Variant
        fields = [
            "id", "variant_id", "var_type"
        ]