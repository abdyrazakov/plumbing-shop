import re

from django import forms

from .models import OrderRequest

PHONE_RE = re.compile(r'^\+?[\d\s\-()]{7,20}$')


class OrderRequestForm(forms.ModelForm):
    class Meta:
        model = OrderRequest
        fields = ['customer_name', 'phone', 'quantity']
        labels = {
            'customer_name': 'Ваше имя',
            'phone': 'Телефон',
            'quantity': 'Количество',
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digit_count = len(re.sub(r'\D', '', phone))
        if not PHONE_RE.match(phone) or not (7 <= digit_count <= 15):
            raise forms.ValidationError('Введите корректный номер телефона.')
        return phone

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError('Укажите количество больше нуля.')
        return quantity
