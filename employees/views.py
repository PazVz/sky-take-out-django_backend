from dj_rest_auth.jwt_auth import set_jwt_cookies, unset_jwt_cookies
from dj_rest_auth.views import (
    LoginView as DefaultLoginView,
)
from dj_rest_auth.views import (
    LogoutView as DefaultLogoutView,
)
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .serializers import CustomLoginResponseSerializer


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
    def logout(self, request):
        response = Response(
            {"code": 1, "msg": "Successfully Logout"},
            status=status.HTTP_200_OK,
        )
        unset_jwt_cookies(response)
        return response

