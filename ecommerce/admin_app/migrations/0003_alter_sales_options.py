# Generated by Django 4.2.8 on 2024-01-10 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0002_sales_orders'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sales',
            options={'ordering': ['date']},
        ),
    ]