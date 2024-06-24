import logging

from django.contrib.auth import get_user_model
from rest_framework import serializers

from applications.utils import to_camel_case, to_snake_case

logger = logging.getLogger(__name__)


class CustomLoginResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="user.pk")
    name = serializers.CharField(source="user.name")
    token = serializers.CharField(source="access")
    username = serializers.CharField(source="user.username")

    class Meta:
        fields = ("id", "name", "token", "userName")


class EmployeeRepresentationSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {to_camel_case(key): value for key, value in representation.items()}


class EmployeeCreationSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = [
            "id_number",
            "name",
            "phone",
            "sex",
            "username",
        ]

    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)


class EmployeeUpdateSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    id_number = serializers.CharField(max_length=18)
    name = serializers.CharField(max_length=32)
    phone = serializers.CharField(max_length=11)
    sex = serializers.CharField(max_length=1)
    username = serializers.CharField()

    def validate_id(self, value):
        if not get_user_model().objects.filter(id=value).exists():
            raise serializers.ValidationError("Employee does not exist")
        return value

    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)



class EmployeePasswordChangeSerializer(serializers.Serializer):

    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)
