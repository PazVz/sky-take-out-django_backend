# Generated by Django 5.0.6 on 2024-05-27 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='id_number',
            field=models.CharField(blank=True, max_length=18, null=True, verbose_name='ID Number'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='phone',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='sex',
            field=models.IntegerField(blank=True, choices=[(1, 'male'), (0, 'female')], null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='status',
            field=models.IntegerField(blank=True, choices=[(1, 'normal'), (0, 'locked')], default=1, null=True, verbose_name='Account Status'),
        ),
    ]
