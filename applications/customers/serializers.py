from rest_framework import serializers

from .models import WechatCostomer


class AuthorizationWechatCostomerLoginSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        auth_code = getattr(attrs, "code")
        query_user = WechatCostomer.objects.filter(code=auth_code)
        if query_user.exists():
            user = query_user.first()
        else:
            user = WechatCostomer.objects.create(code=auth_code)

        setattr(attrs, "user", user)

        return attrs
