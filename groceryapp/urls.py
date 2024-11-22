# groceryapp/urls.py
from django.urls import path
from . import views  # Import your views here

urlpatterns = [
    path("create-product/", views.create_product, name="create-product"),
    path("get-products/", views.get_products, name="get-products"),
    path("add-to-cart/", views.add_to_cart, name="add_to_cart"),
    path("get-cart-products/", views.get_cart_products, name="get-cart-products"),
    path("create-customer/", views.create_customer, name="create-customer"),
    path("login_user/", views.login_user, name="login_user"),
    path("get_all_customers/", views.get_all_customers, name="get_all_customers"),
    path("create-order/", views.create_order, name="create-order"),
    # Add other URLs as necessary
    path("get-orders/", views.get_orders, name="get_orders"),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete-product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
]
