# Generated by Django 4.2.8 on 2024-01-05 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0062_coupons_minimum_purchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupons',
            name='is_expired',
            field=models.BooleanField(default=False, null=True),
        ),
    ]