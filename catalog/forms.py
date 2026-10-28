import re

from django import forms

PHONE_RE = re.compile(r'^\+?[\d\s\-()]{7,20}$')


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, label='Количество')


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(max_length=255, label='Ваше имя')
    phone = forms.CharField(max_length=32, label='Телефон')

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digit_count = len(re.sub(r'\D', '', phone))
        if not PHONE_RE.match(phone) or not (7 <= digit_count <= 15):
            raise forms.ValidationError('Введите корректный номер телефона.')
        return phone
