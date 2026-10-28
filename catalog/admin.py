from django.contrib import admin
from django.db.models import Count, DecimalField, F, Sum
from django.utils.html import format_html

from .models import Category, Order, OrderItem, Product

admin.site.site_header = 'СантехМаркет'
admin.site.site_title = 'СантехМаркет'
admin.site.index_title = 'Управление магазином'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(product_count=Count('product'))

    def product_count(self, obj):
        return obj.product_count
    product_count.admin_order_field = 'product_count'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'name', 'category', 'price', 'stock_quantity', 'stock_status')
    list_display_links = ('name',)
    list_editable = ('stock_quantity',)
    list_filter = ('category',)
    search_fields = ('name',)
    readonly_fields = ('image_preview',)
    fields = ('name', 'category', 'description', 'price', 'stock_quantity', 'image_preview', 'image')

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;object-fit:cover;border-radius:4px;">',
                obj.image.url,
            )
        return '—'
    thumbnail.short_description = 'Фото'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width:200px;">', obj.image.url)
        return '—'
    image_preview.short_description = 'Текущее фото'

    def stock_status(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color:#c3602a;">● Мало</span>')
        return format_html('<span style="color:#3f7a56;">● В наличии</span>')
    stock_status.short_description = 'Статус'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    fields = ('product', 'quantity', 'subtotal')
    readonly_fields = ('product', 'subtotal')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

    def subtotal(self, obj):
        if obj.pk:
            return obj.quantity * obj.product.price
        return '—'
    subtotal.short_description = 'Сумма'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('customer_name', 'phone', 'created_at', 'item_count', 'order_total')
    date_hierarchy = 'created_at'
    search_fields = ('customer_name', 'phone')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            item_count=Count('items'),
            order_total=Sum(
                F('items__quantity') * F('items__product__price'),
                output_field=DecimalField(),
            ),
        )

    def item_count(self, obj):
        return obj.item_count
    item_count.admin_order_field = 'item_count'
    item_count.short_description = 'Товаров'

    def order_total(self, obj):
        return obj.order_total
    order_total.admin_order_field = 'order_total'
    order_total.short_description = 'Сумма заказа'
