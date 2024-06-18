from django.contrib import admin

from .models import Category, Dish, DishFlavor, Setmeal, SetmealDish

# Register your models here.

admin.site.register(Category)
admin.site.register(Dish)
admin.site.register(DishFlavor)
admin.site.register(Setmeal)
admin.site.register(SetmealDish)
