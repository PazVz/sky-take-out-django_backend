from rest_framework.exceptions import APIException
from rest_framework import status


class UserNotFoundException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "User not found."
    default_code = "user_not_found"

class StatusNotRightException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Status code is NOT correct."
    default_code = "status_not_right"


class KeyMissingException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Missing key."
    default_code = "key_missing"

    def __init__(self, key_name=None, detail=None, code=None):
        if key_name:
            self.detail = f"Missing key: {key_name}."
        else:
            self.detail = self.default_detail
        self.code = code if code else self.default_code
