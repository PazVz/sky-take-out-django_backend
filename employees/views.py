import logging

from dj_rest_auth.jwt_auth import set_jwt_cookies, unset_jwt_cookies
from dj_rest_auth.views import (
    LoginView as DefaultLoginView,
)
from dj_rest_auth.views import (
    LogoutView as DefaultLogoutView,
)
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CustomLoginResponseSerializer, EmployeeSerializer

logger = logging.getLogger(__name__)


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

        if not get_user_model().objects.filter(id=_id).exists():
            return Response(
                {"code": 0, "msg": "Username does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            edit_employee = get_user_model().objects.get(id=_id)
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
            edited_employee = get_user_model().objects.get(id=_id)
            data = EmployeeSerializer(edited_employee).data
            return Response(
                {
                    "code": 1,
                    "data": data,
                    "msg": "Edit employee succussfully",
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

        if _id and get_user_model().objects.filter(id=_id).exists():
            return Response(
                {"code": 0, "msg": "Employee already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if _id:
                created_employee = get_user_model().objects.create(
                    id=_id,
                    id_number=id_number,
                    name=name,
                    phone=phone,
                    sex=sex,
                    username=username,
                    createUser=self.request.user,
                    updateUser=self.request.user,
                )
            else:
                created_employee = get_user_model().objects.create(
                    id_number=id_number,
                    name=name,
                    phone=phone,
                    sex=sex,
                    username=username,
                    createUser=self.request.user,
                    updateUser=self.request.user,
                )
        except Exception as e:
            return Response(
                {"code": 0, "msg": f"Failed to create employee: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            data = EmployeeSerializer(created_employee).data
            return Response(
                {
                    "code": 1,
                    "data": data,
                    "msg": "Create employee succussfully",
                },
                status=status.HTTP_200_OK,
            )


class QueryEmployeeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        employee_id = self.kwargs.get("id", None)
        queried_employee = get_user_model().objects.filter(id=employee_id)
        if not queried_employee.exists():
            return Response(
                {"code": 0, "msg": "User not Found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = EmployeeSerializer(queried_employee[0]).data
        return Response(
            {
                "code": 1,
                "data": data,
                "msg": f"Get employee id = {employee_id} Success.",
            }
        )


class ChangeEmployeeStatusView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        employee_status = self.kwargs.get("status", -1)
        employee_id = request.GET.get("id", None)

        if not employee_id:
            return Response(
                {"code": 0, "msg": "Missing employee id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if employee_status not in (0, 1):
            return Response(
                {"code": 0, "msg": "Status code NOT correct."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query_users = get_user_model().objects.filter(id=employee_id)
        if not query_users.exists():
            return Response(
                {"code": 0, "msg": "Employee do Not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = query_users[0]
        msg = ""
        match (user.status, employee_status):
            case (0, 0):
                msg = f"Employee (id = {employee_id}) account was already LOCKED."
            case (1, 1):
                msg = f"Employee (id = {employee_id}) account was already ACTIVATED."
            case (0, 1):
                msg = f"Employee (id = {employee_id}) account was ACTIVATED."
            case (1, 0):
                msg = f"Employee (id = {employee_id}) account was LOCKED."

        user.status = employee_status
        user.updateUser = request.user
        user.save()

        return Response(
            {"code": 1, "data": EmployeeSerializer(user).data, "msg": msg},
            status=status.HTTP_200_OK,
        )


class EditPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        employee_id = request.data.get("empId", None)
        old_password = request.data.get("oldPassword", None)
        new_password = request.data.get("newPassword", None)

        if not all([employee_id, old_password, new_password]):
            return Response(
                {"code": 0, "msg": "Please fill all the fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query_users = get_user_model().objects.filter(id=employee_id)
        if not query_users.exists():
            return Response(
                {"code": 0, "msg": "Employee do Not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = query_users[0]
        if not user.check_password(old_password):
            return Response(
                {"code": 0, "msg": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {
                "code": 1,
                "data": EmployeeSerializer(user).data,
                "msg": "Password changed successfully.",
            },
            status=status.HTTP_200_OK,
        )


class PaginationEmployeeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_custom_pagination(self, page_size):
        class CustomPagination(PageNumberPagination):

            def __init__(self, page_size) -> None:
                self.page_size = page_size
                super().__init__()

            page_size_query_param = "pageSize"
            max_page_size = 100

        return CustomPagination(page_size)

    def get(self, request, *args, **kwargs):
        name = request.query_params.get("name", None)
        page_size = request.query_params.get("pageSize", None)

        if not page_size:
            return Response(
                {"code": 0, "data": {}, "msg": "Please fill all the fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        paginator = self.get_custom_pagination(page_size)
        queryset = get_user_model().objects.all()
        if name:
            queryset = queryset.filter(name__contains=name)

        result_page = paginator.paginate_queryset(queryset, request)
        if result_page is not None:
            serializer = EmployeeSerializer(result_page, many=True)
            response_data = {
                "code": 1,
                "msg": "Successfully fetched employees",
                "data": {
                    "total": queryset.count(),
                    "records": serializer.data,
                },
            }
            return Response(response_data)
