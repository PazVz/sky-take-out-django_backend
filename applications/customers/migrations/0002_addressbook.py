# Generated by Django 5.0.6 on 2024-06-26 16:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consignee', models.CharField(max_length=50)),
                ('sex', models.CharField(blank=True, choices=[('1', 'male'), ('0', 'female')], max_length=1, null=True)),
                ('phone', models.CharField(max_length=11)),
                ('province_code', models.CharField(max_length=12)),
                ('province_name', models.CharField(max_length=32)),
                ('city_code', models.CharField(max_length=12)),
                ('city_name', models.CharField(max_length=32)),
                ('district_code', models.CharField(max_length=12)),
                ('district_name', models.CharField(max_length=32)),
                ('detail', models.CharField(max_length=200)),
                ('label', models.CharField(blank=True, max_length=100, null=True)),
                ('is_default', models.BooleanField(default=False)),
                ('customer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.wechatcostomer')),
            ],
        ),
    ]
