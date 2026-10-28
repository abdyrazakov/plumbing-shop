from django.contrib import admin

from .models import Category, Order, OrderItem, Product


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['customer_name', 'phone', 'created_at']


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(OrderItem)
