# Generated by Django 5.0 on 2023-12-17 05:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0006_product_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_item',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerce.order'),
        ),
    ]
