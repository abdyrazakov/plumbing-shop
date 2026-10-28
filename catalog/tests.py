from decimal import Decimal

from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .forms import OrderRequestForm
from .models import Category, OrderRequest, Product


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

    def test_order_request_created(self):
        order = OrderRequest.objects.create(
            product=self.product,
            customer_name='Jane Doe',
            phone='555-1234',
            quantity=3,
        )
        self.assertIsNotNone(order.created_at)
        self.assertEqual(str(order), 'Jane Doe - Copper Pipe')

    def test_product_deleted_when_category_deleted(self):
        self.category.delete()
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())


class AdminRegistrationTests(TestCase):
    def test_all_models_registered(self):
        self.assertIn(Category, admin.site._registry)
        self.assertIn(Product, admin.site._registry)
        self.assertIn(OrderRequest, admin.site._registry)

    def test_admin_model_options_available(self):
        for model in (Category, Product, OrderRequest):
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

    def test_product_detail_shows_order_form(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertContains(response, 'Отправить заявку')


class OrderRequestFormTests(TestCase):
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

    def test_valid_phone_formats_accepted(self):
        for phone in ['555-1234', '+1 (555) 123-4567', '5551234567']:
            form = OrderRequestForm(data={
                'customer_name': 'Jane Doe',
                'phone': phone,
                'quantity': 2,
            })
            self.assertTrue(form.is_valid(), f'{phone!r} should be valid: {form.errors}')

    def test_invalid_phone_rejected(self):
        form = OrderRequestForm(data={
            'customer_name': 'Jane Doe',
            'phone': 'not-a-phone',
            'quantity': 2,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_zero_quantity_rejected(self):
        form = OrderRequestForm(data={
            'customer_name': 'Jane Doe',
            'phone': '555-1234',
            'quantity': 0,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

    def test_negative_quantity_rejected(self):
        form = OrderRequestForm(data={
            'customer_name': 'Jane Doe',
            'phone': '555-1234',
            'quantity': -3,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

    def test_blank_customer_name_rejected(self):
        form = OrderRequestForm(data={
            'customer_name': '',
            'phone': '555-1234',
            'quantity': 2,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('customer_name', form.errors)


class OrderRequestViewTests(TestCase):
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

    def test_valid_submission_creates_order_and_redirects(self):
        response = self.client.post(reverse('product_detail', args=[self.product.id]), {
            'customer_name': 'Jane Doe',
            'phone': '555-1234',
            'quantity': 3,
        })
        order_request = OrderRequest.objects.get()
        self.assertEqual(order_request.product, self.product)
        self.assertEqual(order_request.customer_name, 'Jane Doe')
        self.assertEqual(order_request.quantity, 3)
        self.assertRedirects(response, reverse('order_thanks', args=[order_request.id]))

    def test_invalid_submission_rerenders_with_errors(self):
        response = self.client.post(reverse('product_detail', args=[self.product.id]), {
            'customer_name': 'Jane Doe',
            'phone': 'not-a-phone',
            'quantity': 3,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(OrderRequest.objects.exists())
        self.assertContains(response, 'корректный номер телефона')

    def test_order_thanks_shows_confirmation(self):
        order_request = OrderRequest.objects.create(
            product=self.product,
            customer_name='Jane Doe',
            phone='555-1234',
            quantity=3,
        )
        response = self.client.get(reverse('order_thanks', args=[order_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, 'Copper Pipe')

    def test_order_thanks_404_for_missing_order(self):
        response = self.client.get(reverse('order_thanks', args=[999]))
        self.assertEqual(response.status_code, 404)
