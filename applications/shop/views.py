from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView


SHOP_STATUS_KEY = "shop_status"


class GetShopStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        shop_status = cache.get(SHOP_STATUS_KEY)
        return Response(
            {"code": 1, "data": shop_status, "msg": "Get shop status successfully"},
            status=status.HTTP_200_OK,
        )


class ChangeShopStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        shop_status = self.kwargs.get("status", 1)
        cache.set(SHOP_STATUS_KEY, shop_status, timeout=None)
        return Response(
            {
                "code": 1,
                "data": shop_status,
                "msg": "Get shop status successfully",
            },
            status=status.HTTP_200_OK,
        )
