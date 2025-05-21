from rest_framework import serializers

from ..models import Severity


class SeveritySerializer(serializers.ModelSerializer):
    """ """

    class Meta:
        model = Severity
        fields = ["id", "severity_number", "consequence"]
