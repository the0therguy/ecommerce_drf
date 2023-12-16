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


class ReviewRetrieve(APIView):
    permission_classes = [IsAuthenticated]

    def get_review(self, review_uuid):
        try:
            return Review.objects.get(review_uuid=review_uuid)
        except Review.DoesNotExist:
            return None

    def put(self, request, review_uuid):
        review = self.get_review(review_uuid=review_uuid)
        if review.user != request.user:
            return Response("You can't edit this review", status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, review_uuid):
        review = self.get_review(review_uuid=review_uuid)
        if review.user != request.user:
            return Response("You can't edit this review", status=status.HTTP_400_BAD_REQUEST)

        review.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
