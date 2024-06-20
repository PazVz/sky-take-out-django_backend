from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView, status

from .serializers import UploadedImageSerializer


class ImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.data.get("file", None)
        if not file:
            return Response(
                {"code": "0", "msg": "No file found in the request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image_serializer = UploadedImageSerializer(data=request.data)

        if image_serializer.is_valid():
            uploaded_image = image_serializer.save()
            return Response(
                {
                    "code": "1",
                    "data": uploaded_image.get_image_path(),
                    "msg": "Image uploaded successfully",
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "code": "0",
                    "msg": f"Image upload failed, error: {image_serializer.errors}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
