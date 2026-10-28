from . import cart

WHATSAPP_NUMBER = '996000000000'


def cart_context(request):
    return {'cart_item_count': cart.total_items(request.session)}


def site_contact(request):
    return {
        'whatsapp_number': WHATSAPP_NUMBER,
        'phone_display': '+996 (000) 00-00-00',
        'phone_href': 'tel:+996000000000',
    }
