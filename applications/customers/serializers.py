import requests
from django.conf import settings
from rest_framework import serializers

from applications.utils import standard_response, to_camel_case, to_snake_case

from .models import WechatCostomer, AddressBook


class AuthorizationWechatCostomerLoginSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        auth_code = attrs.get("code")
        app_id = settings.WECHAT_APPID
        app_secret = settings.WECHAT_SECRET_KEY
        wechat_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={app_id}&secret={app_secret}&js_code={auth_code}&grant_type=authorization_code"
        response = requests.get(wechat_url)
        if response.status_code != 200:
            raise serializers.ValidationError("Failed to authenticate with WeChat")
        wechat_data = response.json()
        if "errcode" in wechat_data:
            raise serializers.ValidationError(wechat_data["errmsg"])
        open_id = wechat_data["openid"]
        user, created = WechatCostomer.objects.get_or_create(openid=open_id)

        attrs["user"] = user

        return attrs


class AddressBookRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressBook
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {to_camel_case(key): value for key, value in representation.items()}


class AddressBookCreationSerializer(serializers.Serializer):
    city_code = serializers.CharField(max_length=12, required=False)
    cite_name = serializers.CharField(max_length=32, required=False)
    consignee = serializers.CharField(max_length=50, required=False)
    detail = serializers.CharField(max_length=200, required=True)
    district_code = serializers.CharField(max_length=12, required=False)
    district_name = serializers.CharField(max_length=32, required=False)
    is_default = serializers.BooleanField(required=False)
    label = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=11, required=True)
    province_code = serializers.CharField(max_length=12, required=False)
    province_name = serializers.CharField(max_length=32, required=False)
    sex = serializers.CharField(max_length=1, required=True)

    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)


class AddressBookUpdateSerializer(serializers.Serializer):
    city_code = serializers.CharField(max_length=12, required=False)
    cite_name = serializers.CharField(max_length=32, required=False)
    consignee = serializers.CharField(max_length=50, required=False)
    detail = serializers.CharField(max_length=200, required=True)
    district_code = serializers.CharField(max_length=12, required=False)
    district_name = serializers.CharField(max_length=32, required=False)
    id = serializers.IntegerField()
    is_default = serializers.BooleanField(required=False)
    label = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=11, required=True)
    province_code = serializers.CharField(max_length=12, required=False)
    province_name = serializers.CharField(max_length=32, required=False)
    sex = serializers.CharField(max_length=1, required=True)

    def validata_id(self, value):
        if not WechatCostomer.objects.filter(id=value).exists():
            raise serializers.ValidationError("User do not exsit.")
        return value

    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)
