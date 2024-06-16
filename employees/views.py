from dj_rest_auth.jwt_auth import set_jwt_cookies, unset_jwt_cookies
from dj_rest_auth.views import (
    LoginView as DefaultLoginView,
)
from dj_rest_auth.views import (
    LogoutView as DefaultLogoutView,
)
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Employee
from .serializers import CustomLoginResponseSerializer, EmployeeSerializer


class CustomLoginView(DefaultLoginView):

    def get_response(self):
        serializer_class = CustomLoginResponseSerializer
        data = {
            "user": self.user,
            "access": self.access_token,
        }

        data["refresh"] = ""
        serializer = serializer_class(
            instance=data,
            context=self.get_serializer_context(),
        )
        response = Response(serializer.data, status=status.HTTP_200_OK)
        set_jwt_cookies(response, self.access_token, self.refresh_token)

        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        try:
            self.serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response(
                {
                    "code": 0,
                    "msg": "Login failed",
                },
                status=status.HTTP_200_OK,
            )
        else:
            self.login()
            return self.get_response()


class CustomLogoutView(DefaultLogoutView):
    permission_classes = [permissions.IsAuthenticated]

    def logout(self, request):
        response = Response(
            {"code": 1, "msg": "Successfully Logout"},
            status=status.HTTP_200_OK,
        )
        unset_jwt_cookies(response)
        return response


class EmployeeView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        self.request = request
        _id = self.request.data.get("id", "")
        id_number = self.request.data.get("idNumber", None)
        name = self.request.data.get("name", None)
        phone = self.request.data.get("phone", None)
        sex = self.request.data.get("sex", None)
        username = self.request.data.get("username", None)

        if not all([_id, id_number, name, phone, sex, username]):
            return Response(
                {"code": 0, "msg": "Please fill all the fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not Employee.objects.filter(id=_id).exists():
            return Response(
                {"code": 0, "msg": "Username does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            edit_employee = Employee.objects.get(id=_id)
            edit_employee.id_number = id_number
            edit_employee.id_number = id_number
            edit_employee.name = name
            edit_employee.phone = phone
            edit_employee.sex = sex
            edit_employee.username = username
            edit_employee.update_user = self.request.user
            edit_employee.save()
        except Exception as e:
            return Response(
                {"code": 0, "msg": f"Failed to edit employee: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            edited_employee = Employee.objects.get(id=_id)
            data = EmployeeSerializer(edited_employee).data
            return Response(
                {
                    "code": 1,
                    "data": data,
                    "msg": "Create or edit employee succussfully",
                }
            )

    def put(self, request, *args, **kwargs):
        self.request = request
        _id = self.request.data.get("id", "")
        id_number = self.request.data.get("idNumber", None)
        name = self.request.data.get("name", None)
        phone = self.request.data.get("phone", None)
        sex = self.request.data.get("sex", None)
        username = self.request.data.get("username", None)

        if not all([id_number, name, phone, sex, username]):
            return Response(
                {"code": 0, "msg": "Please fill all the fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if _id and Employee.objects.filter(id=_id).exists():
            return Response(
                {"code": 0, "msg": "Employee already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if _id:
                Employee.objects.create(
                    id=_id,
                    id_number=id_number,
                    name=name,
                    phone=phone,
                    sex=sex,
                    username=username,
                    create_user=self.request.user,
                    update_user=self.request.user,
                )
            else:
                Employee.objects.create(
                    id_number=id_number,
                    name=name,
                    phone=phone,
                    sex=sex,
                    username=username,
                    create_user=self.request.user,
                    update_user=self.request.user,
                )
        except Exception as e:
            return Response(
                {"code": 0, "msg": f"Failed to create employee: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            if _id:
                created_employee = Employee.objects.get(id=_id)
            else:
                created_employee = Employee.objects.latest("id")
            data = EmployeeSerializer(created_employee).data
            return Response(
                {
                    "code": 1,
                    "data": data,
                    "msg": "Create or edit employee succussfully",
                }
            )
