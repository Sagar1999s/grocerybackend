# Generated by Django 5.1.3 on 2024-11-20 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groceryapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.CharField(max_length=255),
        ),
    ]
