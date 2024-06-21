from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status
from applications.utils import standard_response


def custom_exception_handler(exc, context):

    default_response = drf_exception_handler(exc, context)

    if default_response is None:
        return standard_response(
            False,
            f"An unexpected error occurred: {str(exc)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    else:
        return standard_response(
            False,
            f"An unexpected error occurred: {str(exc)}",
            default_response.data,
            status_code=default_response.status_code,
        )
