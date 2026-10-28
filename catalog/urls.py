from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/<int:category_id>/', views.catalog_view, name='catalog'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('order-thanks/<int:order_id>/', views.order_thanks, name='order_thanks'),
]
