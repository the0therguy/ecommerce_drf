# Generated by Django 5.0 on 2023-12-16 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0003_shop_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='trade_license_no',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]