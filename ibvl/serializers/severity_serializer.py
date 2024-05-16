from rest_framework import serializers

from ibvl.models import (
    Severity
)


class SeveritySerializer(serializers.ModelSerializer):
    """
    """
    class Meta:
        model = Severity
        fields = [
            "id", "severity_number", "consequence"
        ]