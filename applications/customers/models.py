from django.db import models


# Create your models here.
class WechatCostomer(models.Model):
    code = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.auth_code
