# Generated by Django 4.2.8 on 2023-12-26 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0037_alter_productoptions_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productoptions',
            name='product',
            field=models.ManyToManyField(related_name='options', to='user_app.products'),
        ),
    ]
