# Generated by Django 5.1.3 on 2024-11-20 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groceryapp', '0002_alter_product_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
    ]
