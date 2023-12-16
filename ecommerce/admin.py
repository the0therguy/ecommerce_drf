from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(Shop)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Shipping)
