from decimal import Decimal

from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .forms import AddToCartForm, CheckoutForm
from .models import Category, Order, OrderItem, Product
from .templatetags.catalog_extras import ru_product_count
from .views import CATEGORY_ICONS, DEFAULT_CATEGORY_ICON


class ModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Pipes')
        self.product = Product.objects.create(
            name='Copper Pipe',
            description='1-inch copper pipe',
            price=Decimal('19.99'),
            image=SimpleUploadedFile('pipe.jpg', b'fake-image-bytes', content_type='image/jpeg'),
            category=self.category,
            stock_quantity=50,
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Pipes')

    def test_product_created_with_category(self):
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.stock_quantity, 50)
        self.assertEqual(str(self.product), 'Copper Pipe')

    def test_product_deleted_when_category_deleted(self):
        self.category.delete()
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())


class OrderModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Pipes')
        self.product = Product.objects.create(
            name='Copper Pipe',
            description='1-inch copper pipe',
            price=Decimal('19.99'),
            image=SimpleUploadedFile('pipe.jpg', b'fake-image-bytes', content_type='image/jpeg'),
            category=self.category,
            stock_quantity=50,
        )

    def test_order_created(self):
        order = Order.objects.create(customer_name='Jane Doe', phone='555-1234')
        self.assertIsNotNone(order.created_at)
        self.assertIn('Jane Doe', str(order))

    def test_order_item_created_and_rounds_trip(self):
        order = Order.objects.create(customer_name='Jane Doe', phone='555-1234')
        item = OrderItem.objects.create(order=order, product=self.product, quantity=3)
        self.assertEqual(item.order, order)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 3)
        self.assertIn(item, order.items.all())

    def test_order_items_cascade_delete_with_order(self):
        order = Order.objects.create(customer_name='Jane Doe', phone='555-1234')
        OrderItem.objects.create(order=order, product=self.product, quantity=3)
        order.delete()
        self.assertFalse(OrderItem.objects.exists())


class AdminRegistrationTests(TestCase):
    def test_all_models_registered(self):
        self.assertIn(Category, admin.site._registry)
        self.assertIn(Product, admin.site._registry)
        self.assertIn(Order, admin.site._registry)
        self.assertIn(OrderItem, admin.site._registry)

    def test_admin_model_options_available(self):
        for model in (Category, Product, Order, OrderItem):
            self.assertIsNotNone(admin.site._registry[model])


class ViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Pipes')
        self.other_category = Category.objects.create(name='Valves')
        self.product = Product.objects.create(
            name='Copper Pipe',
            description='1-inch copper pipe',
            price=Decimal('19.99'),
            image=SimpleUploadedFile('pipe.jpg', b'fake-image-bytes', content_type='image/jpeg'),
            category=self.category,
            stock_quantity=50,
        )

    def test_home_lists_categories(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pipes')
        self.assertContains(response, 'Valves')

    def test_home_with_no_categories(self):
        Category.objects.all().delete()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Категорий пока нет.')

    def test_catalog_lists_products_for_category(self):
        response = self.client.get(reverse('catalog', args=[self.category.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Copper Pipe')
        self.assertEqual(list(response.context['products']), [self.product])

    def test_catalog_excludes_products_from_other_categories(self):
        response = self.client.get(reverse('catalog', args=[self.other_category.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Copper Pipe')
        self.assertContains(response, 'В этой категории пока нет товаров.')

    def test_catalog_404_for_missing_category(self):
        response = self.client.get(reverse('catalog', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_product_detail_shows_product_info(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Copper Pipe')
        self.assertContains(response, '19.99')
        self.assertContains(response, 'В наличии: 50 шт.')

    def test_product_detail_404_for_missing_product(self):
        response = self.client.get(reverse('product_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_product_detail_shows_add_to_cart_form(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertContains(response, 'Добавить в корзину')


class AddToCartFormTests(TestCase):
    def test_default_quantity_is_one(self):
        form = AddToCartForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(AddToCartForm().fields['quantity'].initial, 1)

    def test_valid_quantity_accepted(self):
        form = AddToCartForm(data={'quantity': 5})
        self.assertTrue(form.is_valid())

    def test_zero_quantity_rejected(self):
        form = AddToCartForm(data={'quantity': 0})
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

    def test_negative_quantity_rejected(self):
        form = AddToCartForm(data={'quantity': -3})
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)


class CheckoutFormTests(TestCase):
    def test_valid_phone_formats_accepted(self):
        for phone in ['555-1234', '+1 (555) 123-4567', '5551234567']:
            form = CheckoutForm(data={
                'customer_name': 'Jane Doe',
                'phone': phone,
            })
            self.assertTrue(form.is_valid(), f'{phone!r} should be valid: {form.errors}')

    def test_invalid_phone_rejected(self):
        form = CheckoutForm(data={
            'customer_name': 'Jane Doe',
            'phone': 'not-a-phone',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_blank_customer_name_rejected(self):
        form = CheckoutForm(data={
            'customer_name': '',
            'phone': '555-1234',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('customer_name', form.errors)


class AddToCartViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Pipes')
        self.product = Product.objects.create(
            name='Copper Pipe',
            description='1-inch copper pipe',
            price=Decimal('19.99'),
            image=SimpleUploadedFile('pipe.jpg', b'fake-image-bytes', content_type='image/jpeg'),
            category=self.category,
            stock_quantity=50,
        )

    def test_add_to_cart_adds_line_and_redirects_to_product(self):
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        self.assertRedirects(response, reverse('product_detail', args=[self.product.id]))
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 2})

    def test_add_to_cart_twice_accumulates_quantity(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 3})
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 5})

    def test_add_to_cart_404_for_missing_product(self):
        response = self.client.post(reverse('add_to_cart', args=[999]), {'quantity': 1})
        self.assertEqual(response.status_code, 404)

    def test_add_to_cart_rejects_get(self):
        response = self.client.get(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 405)
        self.assertNotIn('cart', self.client.session)


class CartViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Pipes')
        self.product = Product.objects.create(
            name='Copper Pipe',
            description='1-inch copper pipe',
            price=Decimal('19.99'),
            image=SimpleUploadedFile('pipe.jpg', b'fake-image-bytes', content_type='image/jpeg'),
            category=self.category,
            stock_quantity=50,
        )
        self.other_product = Product.objects.create(
            name='Steel Valve',
            description='valve',
            price=Decimal('10.00'),
            category=self.category,
            stock_quantity=10,
        )

    def test_empty_cart_shows_empty_state(self):
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Корзина пуста.')

    def test_cart_with_items_shows_subtotals_and_total(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        self.client.post(reverse('add_to_cart', args=[self.other_product.id]), {'quantity': 1})
        response = self.client.get(reverse('cart'))
        self.assertContains(response, 'Copper Pipe')
        self.assertContains(response, 'Steel Valve')
        self.assertContains(response, '39.98')
        self.assertContains(response, '49.98')

    def test_update_cart_item_changes_quantity(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        response = self.client.post(reverse('update_cart_item', args=[self.product.id]), {'quantity': 5})
        self.assertRedirects(response, reverse('cart'))
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 5})

    def test_update_cart_item_to_zero_removes_it(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        self.client.post(reverse('update_cart_item', args=[self.product.id]), {'quantity': 0})
        self.assertEqual(self.client.session['cart'], {})

    def test_remove_cart_item(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        response = self.client.post(reverse('remove_cart_item', args=[self.product.id]))
        self.assertRedirects(response, reverse('cart'))
        self.assertEqual(self.client.session['cart'], {})

    def test_update_cart_item_404_for_missing_product(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        response = self.client.post(reverse('update_cart_item', args=[999]), {'quantity': 5})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 2})

    def test_update_cart_item_rejects_get(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        response = self.client.get(reverse('update_cart_item', args=[self.product.id]), {'quantity': 5})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 2})

    def test_remove_cart_item_rejects_get(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        response = self.client.get(reverse('remove_cart_item', args=[self.product.id]))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 2})


class CheckoutViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Pipes')
        self.product = Product.objects.create(
            name='Copper Pipe',
            description='1-inch copper pipe',
            price=Decimal('19.99'),
            image=SimpleUploadedFile('pipe.jpg', b'fake-image-bytes', content_type='image/jpeg'),
            category=self.category,
            stock_quantity=50,
        )
        self.other_product = Product.objects.create(
            name='Steel Valve',
            description='valve',
            price=Decimal('10.00'),
            category=self.category,
            stock_quantity=10,
        )

    def test_valid_checkout_creates_order_with_items_and_clears_cart(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        self.client.post(reverse('add_to_cart', args=[self.other_product.id]), {'quantity': 1})

        response = self.client.post(reverse('cart'), {
            'customer_name': 'Jane Doe',
            'phone': '555-1234',
        })

        order = Order.objects.get()
        self.assertEqual(order.customer_name, 'Jane Doe')
        self.assertEqual(order.items.count(), 2)
        quantities = {item.product.id: item.quantity for item in order.items.all()}
        self.assertEqual(quantities, {self.product.id: 2, self.other_product.id: 1})
        self.assertRedirects(response, reverse('order_thanks', args=[order.id]))
        self.assertEqual(self.client.session['cart'], {})

    def test_invalid_checkout_rerenders_with_errors_and_preserves_cart(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})

        response = self.client.post(reverse('cart'), {
            'customer_name': 'Jane Doe',
            'phone': 'not-a-phone',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())
        self.assertContains(response, 'корректный номер телефона')
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 2})


class OrderThanksViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Pipes')
        self.product = Product.objects.create(
            name='Copper Pipe',
            description='1-inch copper pipe',
            price=Decimal('19.99'),
            image=SimpleUploadedFile('pipe.jpg', b'fake-image-bytes', content_type='image/jpeg'),
            category=self.category,
            stock_quantity=50,
        )
        self.other_product = Product.objects.create(
            name='Steel Valve',
            description='valve',
            price=Decimal('10.00'),
            category=self.category,
            stock_quantity=10,
        )

    def test_order_thanks_shows_confirmation_with_every_item(self):
        order = Order.objects.create(customer_name='Jane Doe', phone='555-1234')
        OrderItem.objects.create(order=order, product=self.product, quantity=2)
        OrderItem.objects.create(order=order, product=self.other_product, quantity=1)

        response = self.client.get(reverse('order_thanks', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, 'Copper Pipe')
        self.assertContains(response, 'Steel Valve')

    def test_order_thanks_404_for_missing_order(self):
        response = self.client.get(reverse('order_thanks', args=[999]))
        self.assertEqual(response.status_code, 404)


class RuProductCountFilterTests(TestCase):
    def test_singular_form(self):
        self.assertEqual(ru_product_count(1), '1 товар')
        self.assertEqual(ru_product_count(21), '21 товар')

    def test_few_form(self):
        self.assertEqual(ru_product_count(2), '2 товара')
        self.assertEqual(ru_product_count(3), '3 товара')
        self.assertEqual(ru_product_count(4), '4 товара')
        self.assertEqual(ru_product_count(22), '22 товара')

    def test_many_form(self):
        self.assertEqual(ru_product_count(0), '0 товаров')
        self.assertEqual(ru_product_count(5), '5 товаров')
        self.assertEqual(ru_product_count(10), '10 товаров')

    def test_teens_use_many_form_despite_ending_digit(self):
        self.assertEqual(ru_product_count(11), '11 товаров')
        self.assertEqual(ru_product_count(12), '12 товаров')
        self.assertEqual(ru_product_count(14), '14 товаров')


class CategoryIconTests(TestCase):
    def test_known_categories_map_to_dedicated_icons(self):
        self.assertEqual(CATEGORY_ICONS['Трубы и фитинги'], 'catalog/icons/pipes.jpg')
        self.assertEqual(CATEGORY_ICONS['Смесители'], 'catalog/icons/faucet.jpg')
        self.assertEqual(CATEGORY_ICONS['Унитазы и раковины'], 'catalog/icons/toilet.jpg')
        self.assertEqual(CATEGORY_ICONS['Водонагреватели'], 'catalog/icons/heater.jpg')

    def test_unknown_category_falls_back_to_default_icon(self):
        Category.objects.create(name='Неизвестная категория')
        response = self.client.get(reverse('home'))
        self.assertContains(response, DEFAULT_CATEGORY_ICON)

    def test_home_renders_distinct_icon_per_known_category(self):
        for name in CATEGORY_ICONS:
            Category.objects.create(name=name)
        response = self.client.get(reverse('home'))
        for icon_path in CATEGORY_ICONS.values():
            self.assertContains(response, icon_path)


class ProductImageFallbackTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Pipes')

    def test_product_without_image_shows_static_placeholder(self):
        product = Product.objects.create(
            name='No Photo Product',
            description='demo product without a real photo',
            price=Decimal('10.00'),
            category=self.category,
            stock_quantity=1,
        )
        response = self.client.get(reverse('product_detail', args=[product.id]))
        self.assertContains(response, 'catalog/icons/placeholder.jpg')

        catalog_response = self.client.get(reverse('catalog', args=[self.category.id]))
        self.assertContains(catalog_response, 'catalog/icons/placeholder.jpg')

    def test_product_with_image_does_not_show_placeholder(self):
        product = Product.objects.create(
            name='Photographed Product',
            description='demo product with a real photo',
            price=Decimal('10.00'),
            image=SimpleUploadedFile('pipe.jpg', b'fake-image-bytes', content_type='image/jpeg'),
            category=self.category,
            stock_quantity=1,
        )
        response = self.client.get(reverse('product_detail', args=[product.id]))
        self.assertNotContains(response, 'catalog/icons/placeholder.jpg')
