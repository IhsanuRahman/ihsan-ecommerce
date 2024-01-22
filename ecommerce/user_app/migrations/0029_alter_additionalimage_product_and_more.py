# Generated by Django 4.2.8 on 2023-12-19 12:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0028_alter_additionalimage_product_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionalimage',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='user_app.products'),
        ),
        migrations.AlterField(
            model_name='additionalinfo',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='user_app.products'),
        ),
        migrations.AlterField(
            model_name='products',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='user_app.category'),
        ),
        migrations.AlterField(
            model_name='products',
            name='price',
            field=models.FloatField(max_length=50),
        ),
        migrations.AlterField(
            model_name='products',
            name='sub_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='user_app.subcategory'),
        ),
    ]
