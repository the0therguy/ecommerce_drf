from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
import uuid
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal


# Create your views here.

class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    permission_classes = (AllowAny,)


class SigninView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = MyTokenObtainPairSerializer


class LogoutView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def create(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data.get('old_password')
            new_password = serializer.validated_data.get('new_password')

            # Check if the old password matches the current password
            if not check_password(old_password, request.user.password):
                return Response({"message": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

            # Change the password and save the user object
            request.user.set_password(new_password)
            request.user.save()

            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShopGetCreateView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShopSerializer

    def get_queryset(self):
        return Shop.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, shop_uuid=str(uuid.uuid4()))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response("Please register a shop first", status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShopProductListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):
        shop = self.get_shop(owner=self.request.user)
        if shop:
            return Product.objects.filter(shop=shop)
        return Product.objects.none()

    def get_shop(self, owner):
        try:
            return Shop.objects.get(owner=owner)
        except Shop.DoesNotExist:
            return None

    def perform_create(self, serializer):
        shop = self.get_shop(owner=self.request.user)
        if shop:
            serializer.save(shop=shop, product_uuid=str(uuid.uuid4()))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response("Please register a shop first", status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShopProductRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_shop(self, owner):
        try:
            return Shop.objects.get(owner=owner)
        except Shop.DoesNotExist:
            return None

    def get_queryset(self):
        shop = self.get_shop(owner=self.request.user)
        if shop:
            return Product.objects.filter(shop=shop)
        return Product.objects.none()

    def get_object(self):
        queryset = self.get_queryset()
        return generics.get_object_or_404(queryset, product_uuid=self.kwargs['product_uuid'])

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return ProductUpdateSerializer
        return ProductSerializer

    def perform_update(self, serializer):
        serializer.save()  # You may customize this further based on your needs

    def perform_destroy(self, instance):
        instance.delete()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']


class ProductRetrieveView(APIView):
    permission_classes = [AllowAny]

    def get_product(self, product_uuid):
        try:
            return Product.objects.get(product_uuid=product_uuid)
        except Product.DoesNotExist:
            return None

    def get(self, request, product_uuid):
        product = self.get_product(product_uuid=product_uuid)
        if not product:
            return Response("There is no product with this id", status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def get_product(self, product_uuid):
        try:
            return Product.objects.get(product_uuid=product_uuid)
        except Product.DoesNotExist:
            return None

    def get_queryset(self):
        product_uuid = self.kwargs.get('product_uuid')
        product = self.get_product(product_uuid)
        if product:
            return Review.objects.filter(product=product)
        return Review.objects.none()

    def perform_create(self, serializer):
        product_uuid = self.kwargs.get('product_uuid')
        product = self.get_product(product_uuid)
        if product:
            serializer.save(product=product, user=self.request.user)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Authentication required to create a review", status=status.HTTP_401_UNAUTHORIZED)

        return super().post(request, *args, **kwargs)


class ReviewRetrieve(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer

    def put(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            return Response("You can't edit this review", status=status.HTTP_400_BAD_REQUEST)

        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            return Response("You can't delete this review", status=status.HTTP_400_BAD_REQUEST)

        return super().delete(request, *args, **kwargs)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get_product(self, product_uuid):
        try:
            return Product.objects.get(product_uuid=product_uuid)
        except Product.DoesNotExist:
            return None

    def get_order(self, user):
        try:
            return Order.objects.get(customer=user, status='Pending')
        except Order.DoesNotExist:
            return None

    def get_order_item(self, product, order, user):
        try:
            return OrderItem.objects.get(product=product, order=order, customer=user)
        except OrderItem.DoesNotExist:
            return None

    def get(self, request, product_uuid):
        order = self.get_order(user=request.user)
        if not order:
            try:
                order = Order.objects.create(order_uuid=str(uuid.uuid4()), customer=request.user)
                order.save()
            except Exception as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        product = self.get_product(product_uuid=product_uuid)
        if not product:
            return Response('No product found with this id', status=status.HTTP_400_BAD_REQUEST)

        order_item = self.get_order_item(product=product, order=order, user=request.user)
        if not order_item:
            try:
                order_item = OrderItem.objects.create(
                    order_item_uuid=str(uuid.uuid4()),
                    product=product,
                    quantity=1,
                    item_price=Decimal(product.price),  # Convert product price to Decimal
                    order=order,
                    customer=request.user
                )
                order_item.save()

                order.total_price += Decimal(order_item.item_price)  # Convert item_price to Decimal
                order.save()

                return Response(status=status.HTTP_200_OK)
            except Exception as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        previous_price = Decimal(order_item.item_price)  # Convert item_price to Decimal
        previous_quantity = order_item.quantity
        order_item.quantity += 1
        order_item.item_price = Decimal(previous_quantity + 1) * Decimal(
            product.price)  # Convert product price to Decimal
        order.total_price += (Decimal(previous_quantity + 1) * Decimal(product.price)) - previous_price
        order_item.save()
        order.save()

        return Response(status=status.HTTP_200_OK)


class PendingOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get_order(self, user):
        try:
            return Order.objects.get(customer=user, status='Pending')
        except Order.DoesNotExist:
            return None

    def get(self, request):
        order = self.get_order(user=request.user)
        if not order:
            try:
                order = Order.objects.create(**{'order_uuid': str(uuid.uuid4()), 'customer': request.user})
                order.save()
            except Exception as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        order_item_list = OrderItem.objects.filter(order=order, customer=request.user)
        order_item_serializer = OrderItemSerializer(order_item_list, many=True)
        order_serializer = OrderSerializer(order)
        return Response({'order': order_serializer.data, 'order_items': order_item_serializer.data},
                        status=status.HTTP_200_OK)


class OrderItemUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer
    lookup_field = 'order_item_uuid'  # Specify the lookup field

    def get_queryset(self):
        return OrderItem.objects.filter(customer=self.request.user)

    def perform_update(self, serializer):
        quantity = self.request.data.get('quantity', 1)
        if quantity == 0:
            order_item = serializer.instance
            order_item.order.total_price -= order_item.item_price
            order_item.order.save()
            order_item.delete()
        else:
            new_price = quantity * serializer.instance.product.price
            serializer.instance.order.total_price -= serializer.instance.item_price
            serializer.instance.order.total_price += new_price
            serializer.instance.item_price = new_price
            serializer.instance.quantity = quantity
            serializer.save()
            serializer.instance.order.save()

    def perform_destroy(self, instance):
        instance.order.total_price -= instance.item_price
        instance.order.save()
        instance.delete()