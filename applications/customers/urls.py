from django.urls import path, re_path

from .views import (
    AddressView,
    AuthorizationWechatCostomerLoginView,
    DefaultAddressView,
    QueryAddressByIDView,
    QueryAllAddressView,
    ShoppingCartAddView,
    ShoppingCartAllView,
    ShoppingCartCleanView,
    ShoppingCartRemoveView,
)

urlpatterns = [
    path(
        "user/login",
        AuthorizationWechatCostomerLoginView.as_view(),
        name="costomer_login",
    ),
    re_path(
        r"^addressBook/?$",
        AddressView.as_view(),
        name="add_or_edit_or_delete_address",
    ),
    path("addressBook/list", QueryAllAddressView.as_view(), name="query_address_by_id"),
    path(
        "addressBook/<int:id>",
        QueryAddressByIDView.as_view(),
        name="query_address_by_id",
    ),
    path(
        "addressBook/default",
        DefaultAddressView.as_view(),
        name="query_dafault_address",
    ),
    path(
        "shoppingCart/list",
        ShoppingCartAllView.as_view(),
        name="query_shopping_cart_data",
    ),
    path(
        "shoppingCart/add",
        ShoppingCartAddView.as_view(),
        name="add_to_shopping_cart",
    ),
    path(
        "shoppingCart/clean",
        ShoppingCartCleanView.as_view(),
        name="clean_shopping_cart",
    ),
    path(
        "shoppingCart/sub", ShoppingCartRemoveView.as_view(), name="remove_shopping_cart"
    ),
]
