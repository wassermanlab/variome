from rest_framework import serializers

from ..models import Gene


class GeneSerializer(serializers.ModelSerializer):
    """ """

    class Meta:
        model = Gene
        fields = ["id", "short_name"]
