# Generated by Django 5.0.6 on 2024-06-18 08:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dish',
            old_name='category_id',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='dishflavor',
            old_name='dish_id',
            new_name='dish',
        ),
        migrations.RenameField(
            model_name='setmeal',
            old_name='category_id',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='setmealdish',
            old_name='dish_id',
            new_name='dish',
        ),
        migrations.RenameField(
            model_name='setmealdish',
            old_name='setmeal_id',
            new_name='setmeal',
        ),
    ]
