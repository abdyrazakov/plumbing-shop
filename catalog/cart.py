"""Session-backed cart. Nothing outside this module touches request.session
for cart data."""

from dataclasses import dataclass
from decimal import Decimal

from .models import Product

SESSION_KEY = 'cart'


@dataclass
class CartItem:
    product: Product
    quantity: int

    @property
    def subtotal(self):
        return self.product.price * self.quantity


def _read_cart(session):
    """Read-only: never creates/mutates the session, so plain page views
    that don't touch the cart don't force a session row + cookie."""
    return session.get(SESSION_KEY, {})


def _get_cart(session):
    return session.setdefault(SESSION_KEY, {})


def add(session, product_id, quantity=1):
    cart = _get_cart(session)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + quantity
    session.modified = True


def update(session, product_id, quantity):
    cart = _get_cart(session)
    key = str(product_id)
    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity
    session.modified = True


def remove(session, product_id):
    cart = _get_cart(session)
    cart.pop(str(product_id), None)
    session.modified = True


def clear(session):
    session[SESSION_KEY] = {}
    session.modified = True


def total_items(session):
    return sum(item.quantity for item in iter_items(session))


def iter_items(session):
    cart = _read_cart(session)
    products = Product.objects.filter(pk__in=cart.keys())
    items = []
    for product in products:
        quantity = cart.get(str(product.id))
        if quantity:
            items.append(CartItem(product=product, quantity=quantity))
    return items


def grand_total(items):
    return sum((item.subtotal for item in items), Decimal('0'))
