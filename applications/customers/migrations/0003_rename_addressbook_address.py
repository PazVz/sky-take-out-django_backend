# Generated by Django 5.0.6 on 2024-06-26 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_addressbook'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AddressBook',
            new_name='Address',
        ),
    ]