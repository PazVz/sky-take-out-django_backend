# Generated by Django 5.0.6 on 2024-06-18 07:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0010_alter_employee_sex'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='createTime',
            new_name='create_time',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='createUser',
            new_name='create_user',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='updateTime',
            new_name='update_time',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='updateUser',
            new_name='update_user',
        ),
    ]
