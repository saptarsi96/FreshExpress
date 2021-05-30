from accounts.models import UserAddress
from django import forms
from .models import UserAddress

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ['address', 'city', 'pincode']