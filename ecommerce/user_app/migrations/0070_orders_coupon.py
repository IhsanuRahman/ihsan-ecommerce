# Generated by Django 4.2.8 on 2024-01-06 11:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0069_alter_ordercancelldetials_order_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='coupon',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_app.coupons'),
        ),
    ]