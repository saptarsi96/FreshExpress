from orders.models import Order
from django import forms
from django.contrib.auth.models import User



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address', 'city', 'pin_code']

class RatingForm(forms.ModelForm):
    fields = ('order_id','rating')
