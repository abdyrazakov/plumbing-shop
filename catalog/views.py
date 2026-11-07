from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from . import cart
from .forms import AddToCartForm, CheckoutForm
from .models import Category, Order, OrderItem, Product

CATEGORY_ICONS = {
    'Трубы и фитинги': 'catalog/icons/pipes.jpg',
    'Смесители': 'catalog/icons/faucet.jpg',
    'Унитазы и раковины': 'catalog/icons/toilet.jpg',
    'Водонагреватели': 'catalog/icons/heater.jpg',
}
DEFAULT_CATEGORY_ICON = 'catalog/icons/placeholder.jpg'


def home(request):
    categories = list(Category.objects.annotate(product_count=Count('product')))
    for category in categories:
        category.icon_file = CATEGORY_ICONS.get(category.name, DEFAULT_CATEGORY_ICON)
    return render(request, 'catalog/home.html', {'categories': categories})


def catalog_view(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'catalog/catalog.html', {'category': category, 'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = AddToCartForm()
    return render(request, 'catalog/product_detail.html', {'product': product, 'form': form})


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    next_url = request.POST.get('next', '')
    redirect_target = next_url if (
        next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        )
    ) else None

    if 'quantity' in request.POST:
        form = AddToCartForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Некорректное количество.')
            if redirect_target:
                return redirect(redirect_target)
            return redirect('product_detail', product_id=product.id)
        quantity = form.cleaned_data['quantity']
    else:
        quantity = 1

    cart.add(request.session, product.id, quantity)
    messages.success(request, f'«{product.name}» добавлен в корзину.')
    if redirect_target:
        return redirect(redirect_target)
    return redirect('product_detail', product_id=product.id)


def cart_view(request):
    items = cart.iter_items(request.session)
    total = cart.grand_total(items)

    if request.method == 'POST' and items:
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                customer_name=form.cleaned_data['customer_name'],
                phone=form.cleaned_data['phone'],
            )
            OrderItem.objects.bulk_create([
                OrderItem(order=order, product=item.product, quantity=item.quantity)
                for item in items
            ])
            cart.clear(request.session)
            return redirect('order_thanks', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'catalog/cart.html', {'items': items, 'total': total, 'form': form})


@require_POST
def update_cart_item(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    try:
        quantity = int(request.POST.get('quantity', ''))
    except (TypeError, ValueError):
        messages.error(request, 'Некорректное количество.')
        return redirect('cart')
    if quantity < 0:
        messages.error(request, 'Некорректное количество.')
        return redirect('cart')
    cart.update(request.session, product.id, quantity)
    return redirect('cart')


@require_POST
def remove_cart_item(request, product_id):
    cart.remove(request.session, product_id)
    return redirect('cart')


def order_thanks(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'catalog/order_thanks.html', {'order': order})
