from django.urls import path, re_path

from .views import (
    AddressBookView,
    AuthorizationWechatCostomerLoginView,
    QueryAddressBookByID,
    QueryAllAddressBookView,
)

urlpatterns = [
    path(
        "user/login",
        AuthorizationWechatCostomerLoginView.as_view(),
        name="costomer_login",
    ),
    re_path(
        r"^addressBook/?$",
        AddressBookView.as_view(),
        name="add_or_edit_or_delete_address_book",
    ),
    path("addressBook/list", QueryAllAddressBookView.as_view(), name="address_book"),
    path(
        "addressBook/<int:id>",
        QueryAddressBookByID.as_view(),
        name="query_address_book_by_id",
    ),
]
