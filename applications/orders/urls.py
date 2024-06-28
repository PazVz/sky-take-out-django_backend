from django.urls import path

from .views import (
    OrderCancelView,
    OrderComfirmView,
    OrderCompleteView,
    OrderCreateView,
    OrderDeliveryView,
    OrderPaymentView,
    OrderRejectView,
    OrderRepetitionView,
    PaginationOrderByConditionView,
    PaginationOrderHistoryView,
    QueryOrderByIDView,
    QueryOrderStatisticsView,
)

urlpatterns = [
    path("order/submit", OrderCreateView.as_view(), name="order_submit"),
    path("order/payment", OrderPaymentView.as_view(), name="order_payment"),
    path("order/confirm", OrderComfirmView.as_view(), name="order_confirm"),
    path("order/rejection", OrderRejectView.as_view(), name="order_reject"),
    path("order/delivery/<int:id>", OrderDeliveryView.as_view(), name="order_delivery"),
    path("order/complete/<int:id>", OrderCompleteView.as_view(), name="order_complete"),
    path("order/cancel/<int:id>", OrderCancelView.as_view(), name="order_cancel"),
    path("order/details/<int:id>", QueryOrderByIDView.as_view(), name="order_query"),
    path(
        "order/orderDetail/<int:id>", QueryOrderByIDView.as_view(), name="order_query"
    ),
    path(
        "order/historyOrders",
        PaginationOrderHistoryView.as_view(),
        name="order_history",
    ),
    path(
        "order/repetition/<int:id>",
        OrderRepetitionView.as_view(),
        name="order_repetition",
    ),
    path(
        "order/conditionSearch",
        PaginationOrderByConditionView.as_view(),
        name="order_condition",
    ),
    path(
        "order/statistics", QueryOrderStatisticsView.as_view(), name="order_statistics"
    ),
]
