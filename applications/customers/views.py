import logging

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from applications.exceptions import KeyMissingException
from applications.utils import standard_response

from .models import AddressBook
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


class AddressBookView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = AddressBookCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        create_address_book = AddressBook.objects.create(
            customer_id=request.user, **validated_data
        )
        response_data = AddressBookRepresentationSerializer(create_address_book).data
        return standard_response(
            True, "AddressBook created successfully", response_data
        )

    def put(self, request):
        serializer = AddressBookUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        updata_address_book = AddressBook.objects.get(id=validated_data["id"])
        for key, value in validated_data.items():
            setattr(updata_address_book, key, value)
        updata_address_book.save()
        response_data = AddressBookRepresentationSerializer(updata_address_book).data
        return standard_response(
            True, "AddressBook updated successfully", response_data
        )

    def delete(self, request):
        _id = request.query_params.get("id", None)

        if not _id:
            raise KeyMissingException(key_name="id", position="query params")

        address_book = AddressBook.objects.get(id=_id)
        address_book.delete()
        return standard_response(True, "AddressBook deleted successfully", {})


class QueryAllAddressBookView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        address_books = user.addressbook_set.all()
        serializer = AddressBookRepresentationSerializer(address_books, many=True)
        return standard_response(True, "Query successful", serializer.data)


class QueryAddressBookByID(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        _id = self.kwargs.get("id", None)
        dish = AddressBook.objects.get(id=_id)
        return standard_response(
            True,
            "Get dish data successfully",
            AddressBookRepresentationSerializer(dish).data,
        )
