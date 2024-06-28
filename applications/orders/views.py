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
from .serializers import (
    OrderCreationSerializer,
    OrderRrepresentationSerializer,
    OrderRrepresentationSerializer2,
)

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


class OrderCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        _id = self.kwargs.get("id", None)
        order = Order.objects.get(id=_id)
        order.status = 6
        order.cancel_time = datetime.now()
        order.save()

        return standard_response(True, "Order canceled successfully", {})

class OrderComfirmView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        _id = request.data.get("id", None)
        order = Order.objects.get(id=_id)
        order.status = 3
        order.checkout_time = datetime.now()
        order.save()

        return standard_response(True, "Order confirmed successfully", {})


class OrderRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        _id = request.data.get("id", None)
        rejection_reason = request.data.get("rejectionReason")
        order = Order.objects.get(id=_id)
        order.status = 1
        order.rejection_reason = rejection_reason
        order.save()

        return standard_response(True, "Order rejected successfully", {})


class OrderDeliveryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        _id = self.kwargs.get("id", None)
        order = Order.objects.get(id=_id)
        order.status = 4
        order.delivery_time = datetime.now()
        order.save()

        return standard_response(True, "Order delivery successfully", {})

class OrderCompleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        _id = self.kwargs.get("id", None)
        order = Order.objects.get(id=_id)
        order.status = 5
        order.save()

        return standard_response(True, "Order completed successfully", {})

class OrderRepetitionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        _id = self.kwargs.get("id", None)
        prev_order = Order.objects.get(id=_id)
        order_number = f"{str(time.time()).replace(".", "")}{request.user.id}"
        created_order = Order.objects.create(
            number=order_number,
            status=1,
            user_id=request.user,
            address_book_id=prev_order.address_book_id,
            order_time=datetime.now(),
            amount=prev_order.amount,
            phone=prev_order.phone,
            address=prev_order.address,
            user_name=prev_order.user_name,
            consignee=prev_order.consignee,
            estimated_delivery_time=prev_order.estimated_delivery_time,
            delivery_status=prev_order.delivery_status,
            pack_amount=prev_order.pack_amount,
            tableware_number=prev_order.tableware_number,
            tableware_status=prev_order.tableware_status,
            pay_method=prev_order.pay_method,
            remark=prev_order.remark,
        )
        order_details = OrderDetail.objects.filter(order_id=prev_order)
        for order_detail in order_details:
            OrderDetail.objects.create(
                name=order_detail.name,
                image=order_detail.image,
                order_id=created_order,
                dish_id=order_detail.dish_id,
                setmeal_id=order_detail.setmeal_id,
                dish_flavor=order_detail.dish_flavor,
                number=order_detail.number,
                amount=order_detail.amount,
            )
        return standard_response(True, "Order created successfully", {})


class PaginationOrderByConditionView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page_size = request.query_params.get("pageSize", None)
        _status = request.query_params.get("status", None)
        number = request.query_params.get("number", None)
        phone = request.query_params.get("phone", None)

        if not page_size:
            raise KeyMissingException(key_name="pageSize", position="query params")

        paginator = get_custom_pagination(page_size)
        queryset = Order.objects.all().order_by("-order_time")

        if _status:
            queryset = queryset.filter(status=_status)
        if number:
            queryset = queryset.filter(number=number)
        if phone:
            queryset = queryset.filter(phone=phone)

        result_page = paginator.paginate_queryset(queryset, request)
        return standard_response(
            True,
            "Successfully fetched setmeal",
            {
                "total": queryset.count(),
                "records": OrderRrepresentationSerializer2(result_page, many=True).data,
            },
        )


class QueryOrderStatisticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        to_be_confirmed_count = Order.objects.filter(status=2).count()
        confirmed_count = Order.objects.filter(status=3).count()
        delivery_in_progress_count = Order.objects.filter(status=4).count()

        return standard_response(
            True,
            "Successfully fetched setmeal",
            {
                "toBeConfirmed": to_be_confirmed_count,
                "confirmed": confirmed_count,
                "deliveryInProgress": delivery_in_progress_count,
            },
        )

