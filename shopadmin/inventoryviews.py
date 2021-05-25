from django.http.response import HttpResponse
from django.shortcuts import render
from orders.models import Order, OrderItem
from store.models import Merchant, Product,Store, StoreItem
from django.contrib.auth.decorators import login_required
from datetime import date
from .inventoryforms import StoreForm
from django.http import HttpResponseRedirect

@login_required
def storehome(request): #to add or remove the stores
    form = StoreForm(request.POST)
    shops = Store.objects.filter(merchant__user=request.user)
    context = {'form':form,'shops':shops}
    return render(request,'store.html',context)


@login_required
def redirecthome(request): #to add or remove the stores
    #fetch the form
    form = StoreForm(request.POST)
    if form.is_valid():
        #create a merchant account for user if not exists
        try:
            shopowner = Merchant.objects.get(user=request.user)
        except:
            shopowner = Merchant(user=request.user,joindate=date.today())
            shopowner.save()
        # Add extra items to model form and save the shop object
        shop = form.save(commit=False)
        shop.merchant = shopowner
        shop.lat = 0;
        shop.long = 0;
        shop.save()
    #redirect to store page
    return HttpResponseRedirect("store")


@login_required
def inventoryhome(request,storeid): #to add or remove the items from the store
    shop = []
    try:
        shop = Store.objects.get(id=storeid,merchant__user=request.user)
    except:
        return HttpResponseRedirect("../store")
    items = StoreItem.objects.filter(shop=shop)
    context = {'items':items}
    return render(request,'allitems.html',context)


@login_required
def redirectinventory(request): #to add or remove the stores
    orderlist = {}
    allorders = Order.objects.all()
    for singleorder in allorders:
        li = list(OrderItem.objects.filter(order = singleorder).values_list('product__name',flat=True))
        orderlist[singleorder.id] = li
    context = {'li':orderlist}
    return render(request,'index4.html',context)