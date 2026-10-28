from django import template

register = template.Library()


@register.filter
def ru_product_count(count):
    """Render a product count with Russian numeral agreement, e.g. '2 товара'."""
    count = int(count)
    rem100 = count % 100
    rem10 = count % 10
    if 11 <= rem100 <= 14:
        word = 'товаров'
    elif rem10 == 1:
        word = 'товар'
    elif 2 <= rem10 <= 4:
        word = 'товара'
    else:
        word = 'товаров'
    return f'{count} {word}'
