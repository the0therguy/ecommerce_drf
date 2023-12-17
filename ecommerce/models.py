from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import os
import uuid
from django.utils import timezone


# Create your models here.

class User(AbstractUser):
    full_name = models.CharField(max_length=220, null=True, blank=True)
    email = models.EmailField(_('email'), unique=True)

    groups = models.ManyToManyField(Group, blank=True, related_name='custom_users')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='custom_users')

    def __str__(self):
        return self.username


class Shop(models.Model):
    shop_uuid = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=220)
    address = models.TextField()
    trade_license_no = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=15)

    owner = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


def get_product_image_path(instance, filename):
    unique_filename = f"{str(uuid.uuid4())}-{filename}"

    product_uuid = instance.product_uuid
    return f"product_images/{product_uuid}/{unique_filename}"


PRODUCT_CATEGORIES = [
    ('Electronics', 'Electronics'),
    ('Home and Kitchen', 'Home and Kitchen'),
    ('Books', 'Books'),
    ('Toys', 'Toys'),
    ('Sports and Outdoors', 'Sports and Outdoors'),
    ('Beauty and Personal Care', 'Beauty and Personal Care'),
    ('Automotive', 'Automotive')
]


class Product(models.Model):
    product_uuid = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=220)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    category = models.CharField(max_length=220, choices=PRODUCT_CATEGORIES)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=get_product_image_path, null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


PAYMENT_OPTION = [
    ('Cash on Delivery', 'Cash on Delivery'),
    ('Card', 'Card'),
    ('Mobile Payment', 'Mobile Payment')
]

DELIVERY_OPTION = [
    ('Shipping', 'Shipping'),
    ('Pickup', 'Pickup')
]

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Processing', 'Processing'),
    ('Completed', 'Completed'),
]


class Order(models.Model):
    order_uuid = models.CharField(max_length=50, unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_on = models.DateTimeField(auto_now_add=True)
    payment_mode = models.CharField(max_length=100, choices=PAYMENT_OPTION, default='Cash on Delivery')
    delivery_mode = models.CharField(max_length=100, choices=DELIVERY_OPTION, default='Pickup')
    shipping_address = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.customer.username


class OrderItem(models.Model):
    order_item_uuid = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(Product, models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    item_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.order_item_uuid


class Review(models.Model):
    review_uuid = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    ratings = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=2.5)

    def __str__(self):
        if self.product.name:
            return self.product.name
        return self.review_uuid
