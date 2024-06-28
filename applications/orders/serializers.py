from rest_framework import serializers

from applications.customers.models import Address
from applications.utils import to_camel_case, to_snake_case

from .models import Order, OrderDetail


class OrderDetailRepresentationSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderDetail
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["amount"] = float(representation["amount"])
        representation = {
            to_camel_case(key): value for key, value in representation.items()
        }
        return representation


class OrderRrepresentationSerializer(serializers.ModelSerializer):

    order_detail_list = OrderDetailRepresentationSerializer(
        many=True, read_only=True, source="orderdetail_set"
    )

    class Meta:
        model = Order
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["amount"] = float(representation["amount"])
        representation["pack_amount"] = float(representation["pack_amount"])
        representation = {
            to_camel_case(key): value for key, value in representation.items()
        }
        return representation


class OrderRrepresentationSerializer2(serializers.ModelSerializer):

    order_dishes = order_dishes = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"

    def get_order_dishes(self, obj):
        order_details = obj.orderdetail_set.all()
        return ", ".join([f"{detail.name}*{detail.number}" for detail in order_details])

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["amount"] = float(representation["amount"])
        representation["pack_amount"] = float(representation["pack_amount"])
        representation = {
            to_camel_case(key): value for key, value in representation.items()
        }
        return representation


class OrderCreationSerializer(serializers.Serializer):
    address_book_id = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    delivery_status = serializers.IntegerField()
    estimated_delivery_time = serializers.DateTimeField()
    pack_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    pay_method = serializers.IntegerField()
    remark = serializers.CharField(max_length=100, required=False, allow_blank=True)
    tableware_number = serializers.IntegerField()
    tableware_status = serializers.IntegerField()

    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)

