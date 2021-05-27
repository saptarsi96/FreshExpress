from django.http.response import HttpResponse
from django.shortcuts import render
from orders.models import Order, OrderItem
from store.models import Merchant, Product, Store, StoreItem
from django.contrib.auth.decorators import login_required
from datetime import date
from .inventoryforms import StoreForm, StatusForm, StoreItemForm
from django.http import HttpResponseRedirect


@login_required
def storehome(request):  # to add or remove the stores
    form = StoreForm(request.POST)
    shops = Store.objects.filter(merchant__user=request.user)
    context = {'form': form, 'shops': shops}
    return render(request, 'store.html', context)


@login_required
def redirecthome(request):  # to add or remove the stores
    # fetch the form
    form = StoreForm(request.POST)
    if form.is_valid():
        # create a merchant account for user if not exists
        try:
            shopowner = Merchant.objects.get(user=request.user)
        except:
            shopowner = Merchant(user=request.user, joindate=date.today())
            shopowner.save()
        # Add extra items to model form and save the shop object
        shop = form.save(commit=False)
        shop.merchant = shopowner
        shop.lat = 0
        shop.long = 0
        shop.save()
    # redirect to store page
    return HttpResponseRedirect("store")


@login_required
def inventoryhome(request, storeid):  # to add or remove the items from the store
    shop = []
    try:
        shop = Store.objects.get(id=storeid, merchant__user=request.user)
    except:
        return HttpResponseRedirect("../store")
    items = StoreItem.objects.filter(shop=shop)
    form = StoreItemForm(initial={'shop': shop})
    context = {'items': items, 'form': form}
    return render(request, 'allitems.html', context)


@login_required
def redirectinventory(request):  # to add or remove the stores
    form = StatusForm(request.POST)
    if form.is_valid():
        #status = form.cleaned_data['status']
        itemid = form.cleaned_data['productid']
        try:
            shopitem = StoreItem.objects.get(id=itemid)
        except:
            print("item not found")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        print(shopitem)
        shopitem.status = not shopitem.status
        shopitem.save()
    else:
        print("form not valid")
        print(form)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def redirectadditems(request):
    form = StoreItemForm(request.POST)
    if form.is_valid:
        # form is valid now add the items
        item = form.save(commit=False)
        # apply validation if the shop item belongs to the current use before making changes
        if(item.shop.merchant.user == request.user):
            item = StoreItem.objects.get_or_create(
                shop=item.shop, product=item.product)
        else:
            print("shop does not belongs to current user")
    else:
        print("form is invalid")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def redirectremoveitems(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
