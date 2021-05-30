from store.models import Merchant
from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(UserAddress)
class UserAddressAdminsView(admin.ModelAdmin):
    list_display = ['user','address','pincode','city','lat','long']
