# Generated by Django 4.2.8 on 2023-12-26 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0036_remove_productoptions_product_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productoptions',
            name='product',
            field=models.ManyToManyField(to='user_app.products'),
        ),
    ]