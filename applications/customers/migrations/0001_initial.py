# Generated by Django 5.0.6 on 2024-06-26 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WechatCostomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(max_length=45, unique=True)),
                ('name', models.CharField(blank=True, max_length=32, null=True)),
                ('phone', models.CharField(blank=True, max_length=11, null=True)),
                ('sex', models.CharField(blank=True, max_length=1, null=True)),
                ('id_number', models.CharField(blank=True, max_length=18, null=True)),
                ('avatar', models.CharField(blank=True, max_length=500, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]