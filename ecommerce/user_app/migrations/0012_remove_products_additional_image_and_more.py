# Generated by Django 4.2.8 on 2023-12-13 04:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0011_additionalimage_alter_products_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='additional_image',
        ),
        migrations.AddField(
            model_name='additionalimage',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user_app.products'),
        ),
    ]
