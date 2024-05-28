from django.urls import path
from .views import CustomLoginView, CustomLogoutView, AddEmployeeView

urlpatterns = [
    path("/login", CustomLoginView.as_view(), name="employee_login"),
    path("/logout", CustomLogoutView.as_view(), name="employee_logout"),
    path("/", AddEmployeeView.as_view(), name="add_employee")
]
