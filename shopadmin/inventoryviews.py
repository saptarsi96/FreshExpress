from django.http.response import HttpResponse
from django.shortcuts import render
from orders.models import Order, OrderItem
from store.models import Product


def storehome(request): #to add or remove the stores
    orderlist = {}
    allorders = Order.objects.all()
    for singleorder in allorders:
        li = list(OrderItem.objects.filter(order = singleorder).values_list('product__name',flat=True))
        orderlist[singleorder.id] = li
    context = {'li':orderlist}
    return render(request,'index4.html',context)


def inventoryhome(request): #to add or remove the items from the store
    orderlist = {}
    allorders = Order.objects.all()
    for singleorder in allorders:
        li = list(OrderItem.objects.filter(order = singleorder).values_list('product__name',flat=True))
        orderlist[singleorder.id] = li
    context = {'li':orderlist}
    return render(request,'index4.html',context)

