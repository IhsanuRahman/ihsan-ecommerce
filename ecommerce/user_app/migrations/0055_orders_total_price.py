# Generated by Django 4.2.8 on 2024-01-04 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0054_ordercancelldetials_cancelled_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='total_price',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
