from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/<int:category_id>/', views.catalog_view, name='catalog'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('order-thanks/<int:order_id>/', views.order_thanks, name='order_thanks'),
]
