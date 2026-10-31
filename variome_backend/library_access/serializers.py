from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "full_name"]

    def get_full_name(self, obj):
        return obj.get_full_name()


class InvalidSearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(allow_blank=True, trim_whitespace=False)
    selectedAssembly = serializers.CharField(max_length=32, default="GRCh38")
