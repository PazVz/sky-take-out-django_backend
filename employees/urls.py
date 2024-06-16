from django.urls import path

from .views import CustomLoginView, CustomLogoutView, EmployeeView

urlpatterns = [
    path("employee", EmployeeView.as_view(), name="add_or_edit_employee"),
    path("employee/login", CustomLoginView.as_view(), name="employee_login"),
    path("employee/logout", CustomLogoutView.as_view(), name="employee_logout"),
]
