"""One-off demo seed: a few plumbing-store categories/products so the pages
aren't empty for a screenshot walkthrough. Not part of the factory's own
output - written by hand to generate a quick placeholder image + rows."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop.settings")
import django

django.setup()

from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from catalog.models import Category, OrderRequest, Product


FONT_PATH = "/usr/share/fonts/noto/NotoSans-Regular.ttf"


def placeholder_image(label: str) -> ContentFile:
    img = Image.new("RGB", (400, 300), color=(210, 220, 230))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 390, 290], outline=(120, 140, 160), width=3)
    font = ImageFont.truetype(FONT_PATH, 22)
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((400 - text_w) / 2, (300 - text_h) / 2), label, fill=(60, 70, 80), font=font)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return ContentFile(buf.getvalue(), name=f"{label}.jpg")


OrderRequest.objects.all().delete()
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
        product = Product(
            name=name,
            description=desc,
            price=price,
            category=category,
            stock_quantity=stock,
        )
        product.image.save(f"{name}.jpg", placeholder_image(name), save=False)
        product.save()

print(f"Seeded {Category.objects.count()} categories, {Product.objects.count()} products")
