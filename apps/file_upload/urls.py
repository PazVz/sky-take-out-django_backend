from django.urls import path

from .views import ImageUploadView

urlpatterns = [
    path("common/upload", ImageUploadView.as_view(), name="upload_file"),
]
