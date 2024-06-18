from django.conf import settings
from rest_framework.pagination import PageNumberPagination


def to_camel_case(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def get_custom_pagination(page_size):

    class CustomPagination(PageNumberPagination):

        def __init__(self, page_size) -> None:
            self.page_size = page_size
            super().__init__()

        page_size_query_param = settings.PAGE_SIZE_QUERY_PARAM
        max_page_size = settings.MAX_PAGE_SIZE

    return CustomPagination(page_size)


def from_image_url_to_image_relative_path(image_path):
    media_url = settings.MEDIA_URL
    if image_path.startswith(media_url):
        return image_path[len(media_url) :]
