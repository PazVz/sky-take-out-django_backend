from django.urls import path

from .views import GetShopStatusView, ChangeShopStatusView

urlpatterns = [
    path("shop/status", GetShopStatusView.as_view(), name="get_shop_status"),
    path(
        "shop/<int:status>", ChangeShopStatusView.as_view(), name="change_shop_stauts"
    ),
]
