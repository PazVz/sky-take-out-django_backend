from django.db import models

from applications.customers.models import Address, WechatCostomer
from applications.file_upload.models import UploadedImage
from applications.meals.models import Dish, Setmeal

# Create your models here.


class Order(models.Model):
    number = models.CharField(max_length=50, unique=True)
    status = models.IntegerField(
        choices=(
            (1, "unpaid"),
            (2, "unaccepted"),
            (3, "accepted"),
            (4, "distributing"),
            (5, "completed"),
            (6, "canceled"),
        ),
        default=1,
    )
    user_id = models.ForeignKey(WechatCostomer, on_delete=models.CASCADE)
    address_book_id = models.ForeignKey(Address, on_delete=models.CASCADE)
    order_time = models.DateTimeField(auto_now_add=True)
    checkout_time = models.DateTimeField(null=True, blank=True)
    pay_method = models.IntegerField(choices=((1, "wechat"), (2, "alipay")))
    pay_status = models.IntegerField(
        choices=((1, "unpaid"), (2, "paid"), (3, "refunded")), default=1
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remark = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=11, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    user_name = models.CharField(max_length=32, null=True, blank=True)
    consignee = models.CharField(max_length=32, null=True, blank=True)
    cancel_reason = models.CharField(max_length=255, null=True, blank=True)
    rejection_reason = models.CharField(max_length=255, null=True, blank=True)
    cancel_time = models.DateTimeField(null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    delivery_status = models.IntegerField(
        choices=((1, "rightnow"), (0, "adapt delivery time"))
    )
    delivery_time = models.DateTimeField(null=True, blank=True)
    pack_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tableware_number = models.IntegerField()
    tableware_status = models.IntegerField(choices=((1, "yes"), (0, "no")))


class OrderDetail(models.Model):
    name = models.CharField(max_length=32)
    image = models.ForeignKey(UploadedImage, on_delete=models.CASCADE)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish_id = models.ForeignKey(Dish, on_delete=models.CASCADE, null=True, blank=True)
    setmeal_id = models.ForeignKey(
        Setmeal, on_delete=models.CASCADE, null=True, blank=True
    )
    dish_flavor = models.CharField(max_length=32, null=True, blank=True)
    number = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
