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
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.utils import get_custom_pagination, standard_response

from applications.exceptions import (
    KeyMissingException,
    StatusNotRightException,
    UserNotFoundException,
)
from .serializers import (
    CreateEmployeeSerializer,
    CustomLoginResponseSerializer,
    RepresentEmployeeSerializer,
    UpdateEmployeePasswordSerializer,
    UpdateEmployeeSerializer,
)

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
        response = standard_response(True, "Login successful", serializer.data)
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
        response = standard_response(True, "Logout successful")
        unset_jwt_cookies(response)
        return response


class EmployeeView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = CreateEmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        created_employee = get_user_model().objects.create(
            **validated_data,
            create_user=request.user,
            update_user=request.user,
        )
        represent_data = RepresentEmployeeSerializer(created_employee).data
        return standard_response(True, "Employee created successfully", represent_data)

    def put(self, request, *args, **kwargs):
        serializer = UpdateEmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        updated_employee = get_user_model().objects.get(id=validated_data["id"])
        for key, value in validated_data.items():
            setattr(updated_employee, key, value)
        updated_employee.update_user = request.user
        updated_employee.save()
        represent_data = RepresentEmployeeSerializer(updated_employee).data
        return standard_response(True, "Employee updated successfully", represent_data)


class QueryEmployeeByIDView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        employee_id = self.kwargs.get("id", None)
        employee = get_user_model().objects.get(id=employee_id)
        if not employee:
            raise UserNotFoundException

        return standard_response(
            True,
            "Employee fetched successfully",
            RepresentEmployeeSerializer(employee).data,
        )


class ChangeEmployeeStatusView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        employee_status = self.kwargs.get("status", -1)
        employee_id = request.GET.get("id", None)

        if not employee_id:
            raise KeyMissingException(key_name="employeeId")

        if employee_status not in (0, 1):
            raise StatusNotRightException

        user = get_user_model().objects.get(id=employee_id)
        if not user:
            raise UserNotFoundException

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
        user.update_user = request.user
        user.save()

        return standard_response(True, msg)


class EditPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = UpdateEmployeePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = request.user
        user.set_password(validated_data["new_password"])
        user.save()

        return standard_response(True, "Password updated successfully")


class PaginationEmployeeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        name = request.query_params.get("name", None)
        page_size = request.query_params.get("pageSize", None)

        if not page_size:
            raise KeyMissingException(key_name="pageSize")

        paginator = get_custom_pagination(page_size)
        queryset = get_user_model().objects.all()
        if name:
            queryset = queryset.filter(name__contains=name)

        result_page = paginator.paginate_queryset(queryset, request)
        return standard_response(
            True,
            "Successfully fetched employees",
            {
                "total": queryset.count(),
                "records": RepresentEmployeeSerializer(result_page, many=True).data,
            },
        )
