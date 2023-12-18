# Generated by Django 5.0 on 2023-12-16 16:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0004_alter_shop_trade_license_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('Electronics', 'Electronics'), ('Home and Kitchen', 'Home and Kitchen'), ('Books', 'Books'), ('Toys', 'Toys'), ('Sports and Outdoors', 'Sports and Outdoors'), ('Beauty and Personal Care', 'Beauty and Personal Care'), ('Automotive', 'Automotive')], default=datetime.datetime(2023, 12, 16, 16, 24, 4, 764534, tzinfo=datetime.timezone.utc), max_length=220),
            preserve_default=False,
        ),
    ]
