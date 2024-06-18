import logging
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from .views import ImageUploadView

logger = logging.getLogger(__name__)


class FileUploadTestCase(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_upload_image",
            password="testpass123",
            name="test_upload_image",
            phone="12345678901",
            sex="1",
            id_number="123456789012345678",
            status=1,
        )
        self.url = reverse("upload_file")
        self.factory = APIRequestFactory()
        self.view = ImageUploadView.as_view()

    def test_file_upload(self):
        # Create a test image
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'png')
        image_file.seek(0)

        # Create a SimpleUploadedFile from the image file
        file = SimpleUploadedFile("test_file.png", image_file.read(), content_type="image/png")

        request = self.factory.post(self.url, {"file": file})
        force_authenticate(request, self.user)
        response = self.view(request)
        logging.debug(f"msg: {response.data.get("msg", "")}")
        self.assertEqual(response.status_code, 201)

