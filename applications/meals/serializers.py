import logging

from rest_framework import serializers

from applications.utils import (
    to_camel_case,
    to_snake_case,
)

from .models import Category, Dish, DishFlavor, Setmeal, SetmealDish

logger = logging.getLogger(__name__)


class CategoryRepresentationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {to_camel_case(key): value for key, value in representation.items()}


class CategoryCreationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["name", "sort", "type"]

    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)


class CategoryUpdateSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    name = serializers.CharField()
    sort = serializers.IntegerField()

    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)


class DishFlavorRepresentationSerializer(serializers.ModelSerializer):

    class Meta:
        model = DishFlavor
        fields = ["name", "value"]


class DishFlavorAcceptationSerializer(serializers.ModelSerializer):

    class Meta:
        model = DishFlavor
        fields = ["name", "value"]


class DishRepresentationSerializer(serializers.ModelSerializer):

    category_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    flavors = DishFlavorRepresentationSerializer(
        many=True, read_only=True, source="dishflavor_set"
    )

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

    def get_image(self, obj):
        return obj.image.file.url

    def get_category_name(self, obj):
        return obj.category_id.name

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["price"] = float(instance.price) if instance.price else None
        representation = {
            to_camel_case(key): value for key, value in representation.items()
        }
        return representation


class DishCreationSerializer(serializers.ModelSerializer):

    category_id = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)
    flavors = DishFlavorAcceptationSerializer(many=True, required=False)
    image = serializers.CharField()
    status = serializers.IntegerField(required=False)

    class Meta:
        model = Dish
        fields = [
            "category_id",
            "description",
            "flavors",
            "name",
            "price",
            "image",
            "status",
        ]

    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)


class DishUpdateSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)
    flavors = DishFlavorAcceptationSerializer(many=True, required=False)
    id = serializers.IntegerField()
    image = serializers.CharField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.IntegerField(required=False)

    def validate_id(self, value):
        if not Dish.objects.filter(id=value).exists():
            raise serializers.ValidationError("Dish does not exist")
        return value

    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)


class SetmealDishRepresentationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SetmealDish
        fields = ["id", "dish_id", "setmeal_id", "price", "name", "copies"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["price"] = float(instance.price) if instance.price else None
        representation = {
            to_camel_case(key): value for key, value in representation.items()
        }
        return representation


class SetmealDishAcceptationSerializer(serializers.Serializer):
    dish_id = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    name = serializers.CharField()
    copies = serializers.IntegerField()

    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)


class SetmealRepresentationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    setmeal_dishes = SetmealDishRepresentationSerializer(
        many=True, read_only=True, source="setmealdish_set"
    )

    class Meta:
        model = Setmeal
        fields = [
            "id",
            "name",
            "category_id",
            "category_name",
            "price",
            "image",
            "description",
            "status",
            "update_time",
            "setmeal_dishes",
        ]

    def get_image(self, obj):
        return obj.image.file.url

    def get_category_name(self, obj):
        return obj.category_id.name if obj.category_id else None

    def get_setmeal_dishes(self, obj):
        setmeal_dishes = SetmealDish.objects.filter(setmeal_id=obj)
        return SetmealDishRepresentationSerializer(setmeal_dishes, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["price"] = float(instance.price) if instance.price else None
        representation = {
            to_camel_case(key): value for key, value in representation.items()
        }
        return representation


class SetmealCreationSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)
    image = serializers.CharField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.IntegerField(required=False)
    setmeal_dishes = SetmealDishAcceptationSerializer(many=True)

    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)


class SetmealUpdateSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)
    id = serializers.IntegerField()
    image = serializers.CharField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.IntegerField(required=False)
    setmeal_dishes = SetmealDishAcceptationSerializer(many=True)

    def validate_id(self, value):
        if not Setmeal.objects.filter(id=value).exists():
            raise serializers.ValidationError("Setmeal does not exist")
        return value

    def to_internal_value(self, data):
        data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(data)
