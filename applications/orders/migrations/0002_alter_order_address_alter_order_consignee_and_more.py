# Generated by Django 5.0.6 on 2024-06-27 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='consignee',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='pay_status',
            field=models.IntegerField(choices=[(1, 'unpaid'), (2, 'paid'), (3, 'refunded')], default=1),
        ),
        migrations.AlterField(
            model_name='order',
            name='phone',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='user_name',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
