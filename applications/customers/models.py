from django.db import models


# Create your models here.
class WechatCostomer(models.Model):
    openid = models.CharField(max_length=45, unique=True)
    name = models.CharField(max_length=32, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    sex = models.CharField(max_length=1, blank=True, null=True)
    id_number = models.CharField(max_length=18, blank=True, null=True)
    avatar = models.CharField(max_length=500, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.openid

    @property
    def is_authenticated(self):
        return True


class AddressBook(models.Model):
    customer_id = models.ForeignKey(WechatCostomer, on_delete=models.CASCADE)
    consignee = models.CharField(max_length=50)
    sex = models.CharField(
        max_length=1, choices=(("1", "male"), ("0", "female")), null=True, blank=True
    )
    phone = models.CharField(max_length=11)
    province_code = models.CharField(max_length=12)
    province_name = models.CharField(max_length=32)
    city_code = models.CharField(max_length=12)
    city_name = models.CharField(max_length=32)
    district_code = models.CharField(max_length=12)
    district_name = models.CharField(max_length=32)
    detail = models.CharField(max_length=200)
    label = models.CharField(max_length=100, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
