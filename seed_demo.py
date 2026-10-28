"""One-off demo seed: a few plumbing-store categories/products so the pages
aren't empty for a screenshot walkthrough. Not part of the factory's own
output - written by hand to generate the demo rows. Products are left
without a photo; the templates fall back to the static placeholder icon."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop.settings")
import django

django.setup()

from catalog.models import Category, Order, Product


Order.objects.all().delete()
Product.objects.all().delete()
Category.objects.all().delete()

data = {
    "Трубы и фитинги": [
        ("Труба PPR 20мм, 2м", "Полипропиленовая труба для горячего и холодного водоснабжения.", "350.00", 120),
        ("Фитинг-уголок 90° 20мм", "Угловой фитинг для разводки труб PPR.", "45.00", 300),
    ],
    "Смесители": [
        ("Смеситель для кухни Standard", "Однорычажный смеситель, хромированный.", "1800.00", 25),
        ("Смеситель для ванны с душем", "Смеситель с переключателем на лейку душа.", "2600.00", 15),
    ],
    "Унитазы и раковины": [
        ("Унитаз-компакт керамический", "Напольный унитаз с бачком, керамика.", "6200.00", 8),
        ("Раковина накладная 50см", "Керамическая раковина для ванной комнаты.", "2100.00", 12),
    ],
    "Водонагреватели": [
        ("Водонагреватель накопительный 50л", "Электрический бойлер, нержавеющий бак.", "9500.00", 5),
    ],
}

for cat_name, products in data.items():
    category = Category.objects.create(name=cat_name)
    for name, desc, price, stock in products:
        Product.objects.create(
            name=name,
            description=desc,
            price=price,
            category=category,
            stock_quantity=stock,
        )

print(f"Seeded {Category.objects.count()} categories, {Product.objects.count()} products")
