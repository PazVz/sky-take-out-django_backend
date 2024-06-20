from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .forms import EmployeeChangeForm, EmployeeCreationForm
from .models import Employee


class EmployeeAdmin(UserAdmin):
    add_form = EmployeeCreationForm
    form = EmployeeChangeForm
    model = Employee
    list_display = [
        "id",
        "username",
        "name",
        "phone",
        "sex",
        "id_number",
        "status",
        "is_staff",
        "create_time",
        "update_time",
        "create_user",
        "update_user",
    ]
    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                "fields": (
                    "name",
                    "phone",
                    "sex",
                    "id_number",
                    "status",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {
                "fields": (
                    "name",
                    "phone",
                    "sex",
                    "id_number",
                    "status",
                )
            },
        ),
    )

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if not change:
            obj.create_user = request.user
        obj.update_user = request.user
        return super().save_model(request, obj, form, change)


admin.site.register(Employee, EmployeeAdmin)
