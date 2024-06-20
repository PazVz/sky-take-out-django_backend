from django.contrib.auth import get_user_model
from django.db import models

from applications.file_upload.models import UploadedImage

# Create your models here.


class Category(models.Model):
    name = models.CharField(
        max_length=32, unique=True, blank=False, verbose_name="category name"
    )
    type = models.IntegerField(
        choices=[(1, "meal category"), (2, "setmeal category")],
        verbose_name="category type",
    )
    sort = models.IntegerField(unique=True, verbose_name="sort order")
    status = models.IntegerField(
        choices=[(1, "activated"), (0, "banned")], default=1, verbose_name="status"
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="Last Update Time")
    create_user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_category",
        verbose_name="Creator",
    )
    update_user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_category",
        verbose_name="Last Update User",
    )

    def __str__(self) -> str:
        return f"{self.sort}-{self.name}"


class Dish(models.Model):
    name = models.CharField(
        max_length=32, unique=True, blank=False, verbose_name="dish name"
    )
    category_id = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="category",
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, verbose_name="price"
    )
    image = models.ForeignKey(
        UploadedImage,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="image",
    )
    description = models.CharField(max_length=255, verbose_name="description")
    status = models.IntegerField(
        choices=[(1, "activated"), (0, "banned")], default=1, verbose_name="status"
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="Last Update Time")
    create_user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_dish",
        verbose_name="Creator",
    )
    update_user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_dish",
        verbose_name="Last Update User",
    )

    def __str__(self) -> str:
        return self.name


class DishFlavor(models.Model):
    dish_id = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name="dish")
    name = models.CharField(max_length=32, verbose_name="flavor name")
    value = models.CharField(max_length=255, verbose_name="flavor value")

    def __str__(self) -> str:
        return f"{self.dish}-{self.name}"


class Setmeal(models.Model):
    name = models.CharField(
        max_length=32, unique=True, blank=False, verbose_name="setmeal name"
    )
    category_id = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="category",
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, verbose_name="price"
    )
    image = models.ForeignKey(
        UploadedImage,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="image",
    )
    description = models.CharField(max_length=255, verbose_name="description")
    status = models.IntegerField(
        choices=[(1, "activated"), (0, "banned")], default=1, verbose_name="status"
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="Last Update Time")
    create_user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_setmeals",
        verbose_name="Creator",
    )
    update_user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_setmeals",
        verbose_name="Last Update User",
    )

    def __str__(self) -> str:
        return self.name


class SetmealDish(models.Model):
    setmeal_id = models.ForeignKey(Setmeal, on_delete=models.CASCADE)
    dish_id = models.ForeignKey(Dish, on_delete=models.CASCADE)
    copies = models.IntegerField()
    name = models.CharField(max_length=32, verbose_name="dish name", default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="price", default=0.0)

    def __str__(self) -> str:
        return f"{self.setmeal_id}: {self.dish_id} ({self.copies}份)"
