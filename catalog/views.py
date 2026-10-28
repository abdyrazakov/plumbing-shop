from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import OrderRequestForm
from .models import Category, OrderRequest, Product


def home(request):
    categories = Category.objects.annotate(product_count=Count('product'))
    return render(request, 'catalog/home.html', {'categories': categories})


def catalog_view(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'catalog/catalog.html', {'category': category, 'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = OrderRequestForm(request.POST)
        if form.is_valid():
            order_request = form.save(commit=False)
            order_request.product = product
            order_request.save()
            return redirect('order_thanks', order_id=order_request.id)
    else:
        form = OrderRequestForm()
    return render(request, 'catalog/product_detail.html', {'product': product, 'form': form})


def order_thanks(request, order_id):
    order_request = get_object_or_404(OrderRequest, pk=order_id)
    return render(request, 'catalog/order_thanks.html', {'order_request': order_request})
