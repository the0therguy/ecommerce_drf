from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Customizes JWT default Serializer to add more information about user"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class ShopSerializer(serializers.ModelSerializer):
    shop_uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = Shop
        fields = '__all__'


class UpdateShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'
        read_only_fields = ('shop_uuid', 'owner')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'username']


class ProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source="shop.name", read_only=True)
    product_uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductUpdateSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source="shop.name", read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('shop', 'product_uuid')


class ReviewSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    user = ProfileSerializer()

    class Meta:
        model = Review
        fields = '__all__'


class ReviewUpdateSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    user = ProfileSerializer()

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('user', 'product', 'review_uuid')


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    order_item_uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    order_uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
