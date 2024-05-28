from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class Employee(AbstractUser):
    name = models.CharField(max_length=32)
    phone = models.CharField(
        max_length=11, verbose_name="Phone Number", null=True, blank=True
    )
    sex = models.IntegerField(
        choices=((1, "male"), (0, "female")), null=True, blank=True
    )
    id_number = models.CharField(
        max_length=18, verbose_name="ID Number", null=True, blank=True
    )
    status = models.IntegerField(
        choices=[(1, "normal"), (0, "locked")],
        default=1,
        verbose_name="Account Status",
        null=True,
        blank=True,
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="Last Update Time")
    create_user = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_employees",
        verbose_name="Creator",
    )
    update_user = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_employees",
        verbose_name="Last Update User",
    )
