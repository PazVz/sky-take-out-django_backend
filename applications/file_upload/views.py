from rest_framework import permissions
from rest_framework.views import APIView

from applications.exceptions import KeyMissingException
from applications.utils import standard_response

from .serializers import UploadedImageSerializer


class ImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.data.get("file", None)
        if not file:
            raise KeyMissingException(key_name="file")

        image_serializer = UploadedImageSerializer(data=request.data)
        image_serializer.is_valid()
        uploaded_image = image_serializer.save()
        return standard_response(
            True,
            "Image uploaded successfully",
            uploaded_image.get_image_path(),
        )
