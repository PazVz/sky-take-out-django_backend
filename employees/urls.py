from django.urls import path

from .views import (
    CustomLoginView,
    CustomLogoutView,
    EmployeeView,
    QueryEmployeeView,
    ChangeEmployeeStatusView,
    EditPasswordView,
    PaginationEmployeeView,
)

urlpatterns = [
    path("employee", EmployeeView.as_view(), name="add_or_edit_employee"),
    path("employee/login", CustomLoginView.as_view(), name="employee_login"),
    path("employee/logout", CustomLogoutView.as_view(), name="employee_logout"),
    path("employee/<int:id>", QueryEmployeeView.as_view(), name="query_employee"),
    path(
        "employee/status/<int:status>",
        ChangeEmployeeStatusView.as_view(),
        name="change_employee_status",
    ),
    path("employee/editPassword", EditPasswordView.as_view(), name="edit_password"),
    path("employee/page", PaginationEmployeeView.as_view(), name="pagination_employee"),
]
