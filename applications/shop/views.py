from django.core.cache import cache
from rest_framework import permissions
from rest_framework.views import APIView

from applications.utils import standard_response

SHOP_STATUS_KEY = "shop_status"


class GetShopStatusView(APIView):

    def get(self, request, *args, **kwargs):
        shop_status = cache.get(SHOP_STATUS_KEY, 0)
        return standard_response(True, "Get shop status successfully", shop_status)


class ChangeShopStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        shop_status = self.kwargs.get("status", 1)
        cache.set(SHOP_STATUS_KEY, shop_status, timeout=None)
        return standard_response(True, "Change shop status successfully", shop_status)
