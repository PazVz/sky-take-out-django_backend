from django.db import models

# Create your models here.


class UploadedImage(models.Model):
    file = models.ImageField(upload_to="images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_image_path(self):
        return self.file.url

    def __str__(self) -> str:
        return self.file.name
