from django.urls import path

from .views import (
    CancelOrderView,
    OrderCreateView,
    OrderPaymentView,
    PaginationOrderHistoryView,
    QueryOrderByIDView,
)

urlpatterns = [
    path("order/submit", OrderCreateView.as_view(), name="order_submit"),
    path("order/payment", OrderPaymentView.as_view(), name="order_payment"),
    path(
        "order/orderDetail/<int:id>", QueryOrderByIDView.as_view(), name="order_query"
    ),
    path(
        "order/historyOrders",
        PaginationOrderHistoryView.as_view(),
        name="order_history",
    ),
    path("order/cancel/<int:id>", CancelOrderView.as_view(), name="order_cancel"),
]
