from django.http.response import HttpResponse
from django.shortcuts import render
from orders.models import Order, OrderItem
from store.models import Product
from .inventoryviews import *
# Create your views here.

def index(request):
    orderlist = {}
    allorders = Order.objects.all()
    for singleorder in allorders:
        li = list(OrderItem.objects.filter(order = singleorder).values_list('product__name',flat=True))
        orderlist[singleorder.id] = li
    context = {'li':orderlist}
    return render(request,'index4.html',context)