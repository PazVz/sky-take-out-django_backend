from rest_framework import serializers
from .models import UploadedImage


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ("file", "uploaded_at")

    def validate_image(self, value):
        if not value.name.endswith(("jpg", "jpeg", "png")):
            raise serializers.ValidationError(
                "Only jpg, jpeg, and png files are allowed."
            )
        return value
