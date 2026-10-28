from . import cart


def cart_context(request):
    return {'cart_item_count': cart.total_items(request.session)}
