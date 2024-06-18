import logging

from rest_framework import serializers

from utils import to_camel_case

from .models import Category, Dish, DishFlavor

logger = logging.getLogger(__name__)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {to_camel_case(key): value for key, value in representation.items()}


class DishFlavorSerializer(serializers.ModelSerializer):

    class Meta:
        model = DishFlavor
        fields = "__all__"


class DishSerializer(serializers.ModelSerializer):

    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    category_name = serializers.SerializerMethodField()
    flavors = DishFlavorSerializer(many=True, read_only=True, source="dishflavor_set")

    class Meta:
        model = Dish
        fields = [
            "id",
            "name",
            "category_id",
            "category_name",
            "price",
            "image",
            "description",
            "status",
            "flavors",
            "update_time",
        ]

    def get_image_url(self, obj):
        return obj.image.file.url

    def get_category_name(self, obj):
        return obj.category_id.name

    def get_float_price(self, obj):
        return float(obj.price) if obj.price else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["image"] = self.get_image_url(instance)
        representation["category_name"] = self.get_category_name(instance)
        representation["price"] = self.get_float_price(instance)
        representation = {
            to_camel_case(key): value for key, value in representation.items()
        }
        return representation
