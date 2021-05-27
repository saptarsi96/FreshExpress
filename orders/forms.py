from orders.models import Order, Review
from django import forms
from django.contrib.auth.models import User


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address', 'city', 'pin_code']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['userrating']
