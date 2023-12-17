from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from .views import *

urlpatterns = [
    path('api/account/v1/signup/', SignUpView.as_view(), name='signup'),
    path('api/account/v1/signin/', SigninView.as_view(), name='token_obtain_pair'),
    path('api/account/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/account/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/account/v1/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/account/v1/logout/', LogoutView.as_view(), name='auth_logout'),
    path('api/account/v1/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/shop/v1/shop/', ShopGetCreateView.as_view(), name='shop-get-create-update-delete'),
    path('api/shop/v1/products/', ShopProductListView.as_view(), name='product-list-create'),
    path('api/shop/v1/product/<str:product_uuid>/', ShopProductRetrieveUpdateView.as_view(),
         name='product-get-update-delete'),
    path('api/product/v1/products/', ProductViewSet.as_view({'get': 'list'}), name='product-list'),
    path('api/product/v1/product/<str:product_uuid>/', ProductRetrieveView.as_view(), name='product'),
    path('api/reviews/v1/reviews/<str:product_uuid>/', ReviewList.as_view(), name='reviews'),
    path('api/reviews/v1/review/<str:review_uuid>/', ReviewRetrieve.as_view(), name='review'),
    path('api/order/v1/add-to-cart/<str:product_uuid>/', AddToCartView.as_view()),
    path('api/order/v1/order-confirm/', PendingOrderView.as_view()),
    path('api/order/v1/order-item/<str:order_item_uuid>/', OrderItemUpdateDelete.as_view())
]
