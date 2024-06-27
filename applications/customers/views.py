import logging
from datetime import datetime

from django.core.cache import cache
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from applications.exceptions import KeyMissingException
from applications.meals.models import Dish, Setmeal
from applications.utils import standard_response

from .models import Address
from .serializers import (
    AddressBookCreationSerializer,
    AddressBookRepresentationSerializer,
    AddressBookUpdateSerializer,
    AuthorizationWechatCostomerLoginSerializer,
)

logger = logging.getLogger(__name__)


class AuthorizationWechatCostomerLoginView(APIView):

    permission_classes = (permissions.AllowAny,)
    serializer_class = AuthorizationWechatCostomerLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return standard_response(
            True,
            "Login successful",
            {"id": user.pk, "openid": user.openid, "token": str(access_token)},
        )


class AddressView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = AddressBookCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        create_address = Address.objects.create(
            customer_id=request.user, **validated_data
        )
        response_data = AddressBookRepresentationSerializer(create_address).data
        return standard_response(
            True, "AddressBook created successfully", response_data
        )

    def put(self, request):
        serializer = AddressBookUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        updata_address = Address.objects.get(id=validated_data["id"])
        for key, value in validated_data.items():
            setattr(updata_address, key, value)
        updata_address.save()
        response_data = AddressBookRepresentationSerializer(updata_address).data
        return standard_response(
            True, "AddressBook updated successfully", response_data
        )

    def delete(self, request):
        _id = request.query_params.get("id", None)

        if not _id:
            raise KeyMissingException(key_name="id", position="query params")

        address = Address.objects.get(id=_id)
        address.delete()
        return standard_response(True, "AddressBook deleted successfully", {})


class QueryAllAddressView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        address = user.address_set.all()
        serializer = AddressBookRepresentationSerializer(address, many=True)
        return standard_response(True, "Query successful", serializer.data)


class QueryAddressByIDView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        _id = self.kwargs.get("id", None)
        address = Address.objects.get(id=_id)
        return standard_response(
            True,
            "Get dish data successfully",
            AddressBookRepresentationSerializer(address).data,
        )


class DefaultAddressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        default_address_set = Address.objects.filter(
            customer_id=request.user, is_default=True
        )
        default_address = (
            default_address_set.first() if default_address_set.exists() else None
        )
        response_data = (
            AddressBookRepresentationSerializer(default_address).data
            if default_address
            else {}
        )
        return standard_response(
            True, "Get default address successfully", response_data
        )

    def put(self, request):
        _id = request.data.get("id")
        if not _id:
            raise KeyMissingException(key_name="id", position="request body")

        default_address_set = Address.objects.filter(
            customer_id=request.user, is_default=True
        )
        original_default_address = (
            default_address_set.first() if default_address_set.exists() else None
        )
        curr_default_address = Address.objects.get(id=_id)
        curr_default_address.is_default = True
        curr_default_address.save()
        if original_default_address:
            original_default_address.is_default = False
            original_default_address.save()
        return standard_response(True, "Set default address successfully", {})


class ShoppingCartAllView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        cache_key = f"cart_{user_id}"
        cart_data = cache.get(cache_key, {})
        res = []
        for key, value in cart_data.items():
            shopping_cart_item = {}
            shopping_cart_item["number"] = value["count"]
            shopping_cart_item["createTime"] = value["timestamp"]
            match key.split("_"):
                case ["dish", dish_id, dish_flavor]:
                    shopping_cart_item["dishId"] = dish_id
                    shopping_cart_item["dish_flavor"] = dish_flavor
                    dish_obj = Dish.objects.get(id=dish_id)
                    shopping_cart_item["image"] = dish_obj.image.file.url
                    shopping_cart_item["name"] = dish_obj.name
                    shopping_cart_item["amount"] = dish_obj.price
                case ["dish", dish_id, dish_flavor]:
                    shopping_cart_item["dishId"] = dish_id
                    dish_obj = Dish.objects.get(id=dish_id)
                    shopping_cart_item["image"] = dish_obj.image.file.url
                    shopping_cart_item["name"] = dish_obj.name
                    shopping_cart_item["amount"] = dish_obj.price
                case ["setmeal", setmeal_id]:
                    shopping_cart_item["setmeal_id"] = setmeal_id
                    setmeal_obj = Setmeal.objects.get(id=setmeal_id)
                    shopping_cart_item["image"] = setmeal_obj.image.file.url
                    shopping_cart_item["name"] = setmeal_obj.name
                    shopping_cart_item["amount"] = setmeal_obj.price
                case _:
                    raise Exception("idk")
            res.append(shopping_cart_item)
        return standard_response(True, "Get shopping cart data successfully", res)


class ShoppingCartAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        data = self.request.data
        cache_key = f"cart_{user_id}"
        cart_data = cache.get(cache_key, {})

        match data:
            case {"dishId": dish_id, "dishFlavor": dish_flavor}:
                logger.debug(111111)
                item_name = f"dish_{dish_id}_{dish_flavor}"
            case {"dishId": dish_id}:
                logger.debug(222222)
                item_name = f"dish_{dish_id}"
            case {"setmealId": setmeal_id}:
                item_name = f"setmeal_{setmeal_id}"
            case _:
                raise KeyMissingException(
                    key_name="dishId or setmealId", position="request body"
                )

        if item_name in cart_data:
            cart_data[item_name]["count"] += 1
        else:
            cart_data[item_name] = {
                "count": 1,
            }

        cart_data[item_name]["timestamp"] = datetime.now().isoformat()
        cache.set(cache_key, cart_data, timeout=86400)

        return standard_response(True, "Add to shopping cart successfully", {})


class ShoppingCartRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        data = self.request.data
        cache_key = f"cart_{user_id}"
        cart_data = cache.get(cache_key, {})

        match data:
            case {"dishId": dish_id, "dishFlavor": dish_flavor}:
                item_id = f"dish_{dish_id}_{dish_flavor}"
            case {"dishId": dish_id}:
                item_id = f"dish_{dish_id}"
            case {"setmealId": setmeal_id}:
                item_id = f"setmeal_{setmeal_id}"
            case _:
                raise KeyMissingException(
                    key_name="dishId or setmealId", position="request body"
                )

        if item_id not in cart_data or cart_data[item_id]["count"] == 0:
            raise Exception("Item not in shopping cart")

        if cart_data[item_id]["count"] == 1:
            del cart_data[item_id]
        else:
            cart_data[item_id]["count"] -= 1
            cart_data[item_id]["timestamp"] = datetime.now().isoformat()

        cache.set(cache_key, cart_data, timeout=86400)

        return standard_response(True, "Remove from shopping cart successfully", {})


class ShoppingCartCleanView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user_id = self.request.user.id
        cache_key = f"cart_{user_id}"
        cache.delete(cache_key)

        return standard_response(True, "Clean shopping cart successfully", {})
