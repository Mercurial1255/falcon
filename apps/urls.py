from django.urls import path
from django.contrib.auth.views import LoginView

from apps.views import ProductList, ProductDetailView, RegisterCreateView, LogoutView, SettingsUpdateView, \
    CheckoutListView, CartListView, OrderListView, AddToCartView, CartDeleteView, OrderCreateView, \
    AddressCreateView, AddressUpdateView, OrderDetailView

urlpatterns = [
    path('', ProductList.as_view(), name='product_list_page'),
    path('product-detail/<int:pk>/', ProductDetailView.as_view(), name='product_detail_page'),

    path('shopping/cart/', CartListView.as_view(), name='shopping_cart_page'),
    path('card/add/<int:pk>/', AddToCartView.as_view(), name='add_to_cart_page'),
    path('checkout/', CheckoutListView.as_view(), name='checkout_page'),
    path('cart/remove/<int:pk>/', CartDeleteView.as_view(), name='remove_item'),

    path('settings/', SettingsUpdateView.as_view(), name='settings_page'),
    path('login/', LoginView.as_view(
        template_name='apps/auth/login.html',
        redirect_authenticated_user=True,
        next_page='product_list_page',
    ), name='login_page'),
    path('register/', RegisterCreateView.as_view(), name='register_page'),
    path('logout/', LogoutView.as_view(), name='logout_page'),

    path('order-details/<int:pk>', OrderDetailView.as_view(), name='order_detail_page'),
    path('order-list/', OrderListView.as_view(), name='order_list_page'),
    path('order-create/', OrderCreateView.as_view(), name='order_create'),

    path('address-create/', AddressCreateView.as_view(), name='address_create'),
    path('address-update/<int:pk>', AddressUpdateView.as_view(), name='address_update')
]
