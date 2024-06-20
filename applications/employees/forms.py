from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Employee


class EmployeeCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = Employee
        fields = UserCreationForm.Meta.fields + (
            "name",
            "phone",
            "sex",
            "id_number",
            "status",
        )


class EmployeeChangeForm(UserChangeForm):
    class Meta:
        model = Employee
        fields = UserChangeForm.Meta.fields
