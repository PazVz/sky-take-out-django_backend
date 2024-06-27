import logging
import time
from datetime import datetime

from django.core.cache import cache
from rest_framework import permissions
from rest_framework.views import APIView

from applications.exceptions import KeyMissingException
from applications.meals.models import Dish, Setmeal
from applications.utils import get_custom_pagination, standard_response

from .models import Order, OrderDetail
from .serializers import OrderCreationSerializer, OrderRrepresentationSerializer

logger = logging.getLogger(__name__)


class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = OrderCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        curr_time = str(time.time()).replace(".", "")
        order_number = f"{curr_time}{request.user.id}"
        created_order = Order.objects.create(
            **validated_data,
            user_id=request.user,
            number=order_number,
            phone=validated_data["address_book_id"].phone,
            address=str(validated_data["address_book_id"]),
            user_name=request.user.name,
            consignee=validated_data["address_book_id"].consignee,
        )
        cart_items = cache.get(f"cart_{request.user.id}")
        cache.delete(f"cart_{request.user.id}")
        for key, value in cart_items.items():
            match key.split("_"):
                case ["dish", dish_id, *_]:
                    dish = Dish.objects.get(id=dish_id)
                    OrderDetail.objects.create(
                        name=dish.name,
                        image=dish.image,
                        order_id=created_order,
                        dish_id=dish,
                        number=value["number"],
                        amount=dish.price,
                    )
                case ["setmeal", setmeal_id, *_]:
                    setmeal = Setmeal.objects.get(id=setmeal_id)
                    OrderDetail.objects.create(
                        name=setmeal.name,
                        image=setmeal.image,
                        order_id=created_order,
                        setmeal_id=setmeal,
                        number=value["number"],
                        amount=setmeal.price,
                    )

        return standard_response(
            True,
            "Order created successfully",
            {
                "id": created_order.id,
                "orderAmount": created_order.amount,
                "orderNumber": created_order.number,
                "orderTime": created_order.order_time,
            },
        )


class OrderPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        order_number = request.data.get("orderNumber")
        pay_method = request.data.get("payMethod")
        order = Order.objects.get(number=order_number)
        order.pay_method = pay_method
        order.status = 2  # unaccepted
        order.pay_status = 2  # paid
        order.save()

        return standard_response(
            True,
            "Order paid successfully",
            {"estimatedDeliveryTime": order.estimated_delivery_time},
        )


class QueryOrderByIDView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        _id = self.kwargs.get("id", None)
        order = Order.objects.get(id=_id)
        return standard_response(
            True,
            "Get order data successfully",
            OrderRrepresentationSerializer(order).data,
        )


class PaginationOrderHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page_size = request.query_params.get("pageSize", None)
        _status = request.query_params.get("status", None)

        if not page_size:
            raise KeyMissingException(key_name="pageSize", position="query params")

        paginator = get_custom_pagination(page_size)
        queryset = Order.objects.filter(user_id=request.user).order_by("-order_time")

        if _status:
            queryset = queryset.filter(status=_status)

        result_page = paginator.paginate_queryset(queryset, request)

        return standard_response(
            True,
            "Successfully fetched setmeal",
            {
                "total": queryset.count(),
                "records": OrderRrepresentationSerializer(result_page, many=True).data,
            },
        )


class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        _id = self.kwargs.get("id", None)
        order = Order.objects.get(id=_id)
        order.status = 6
        order.cancel_time = datetime.now()
        order.save()

        return standard_response(True, "Order canceled successfully", {})
