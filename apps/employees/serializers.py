from django.contrib.auth import get_user_model
from rest_framework import serializers
from utils import to_camel_case


class CustomLoginResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="user.pk")
    name = serializers.CharField(source="user.name")
    token = serializers.CharField(source="access")
    username = serializers.CharField(source="user.username")

    class Meta:
        fields = ("id", "name", "token", "userName")

    def to_representation(self, instance):
        response_data = super().to_representation(instance)
        return {"code": 1, "data": response_data, "msg": "Login successful"}


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "password",
            "name",
            "phone",
            "sex",
            "id_number",
            "status",
            "create_time",
            "update_time",
            "create_user",
            "update_user",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {to_camel_case(key): value for key, value in representation.items()}
