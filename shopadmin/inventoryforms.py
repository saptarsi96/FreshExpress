from django.db.models import fields
from django.forms import ModelForm
from store.models import Store

class StoreForm(ModelForm):
    class Meta:
        model = Store
        fields = '__all__'
        exclude = ['merchant','lat','long','rating','shop_status','total_orders']
