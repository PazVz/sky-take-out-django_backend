import logging

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from .models import WechatCostomer

logger = logging.getLogger(__name__)


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        auth = request.headers.get("authentication")
        if not auth:
            return None

        try:
            validated_token = self.get_validated_token(auth)
            user = self.get_user(validated_token)
        except InvalidToken:
            return None

        return (user, validated_token)

    def get_user(self, validated_token):
        try:
            user_id = validated_token["user_id"]
            user = WechatCostomer.objects.get(id=user_id)

        except WechatCostomer.DoesNotExist:
            raise InvalidToken("User not found")

        return user
