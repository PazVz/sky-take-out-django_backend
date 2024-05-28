from rest_framework import serializers
# from django.contrib.auth import get_user_model


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
