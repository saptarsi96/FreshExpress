from django.http.response import HttpResponse
from django.shortcuts import render
from orders.models import Order, OrderItem
from store.models import Merchant, Product, Store, StoreItem
from django.contrib.auth.decorators import login_required
from datetime import date
from .inventoryforms import StoreForm, StatusForm, StoreItemForm
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib import messages

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
        try:
            shop2 = Store.objects.filter(merchant__user=request.user)[0]
            shop2.name = shop.name
            shop2.adress = shop.address
            shop2.contact = shop.contact
            shop2.start = shop.start
            shop2.end = shop.end
            shop2.gst = shop.gst
            shop2.save()
            messages.success(request, 'Successfully updated the store information.')
        except:
            shop.merchant = shopowner
            shop.lat = 0
            shop.long = 0
            shop.save()
            messages.success(request, 'You have successfully registered as merchant with below store information.')
    # redirect to store page
    try:
        shop = Store.objects.filter(merchant__user=request.user)[0]
        form = StoreForm(initial={'name':shop.name,'address':shop.address,'contact':shop.contact,'start':shop.start,'end':shop.end,'gst':shop.gst})
    except:
        pass
    context = {'form':form}
    return render(request, 'storeinfo.html', context)


@login_required
def inventoryhome(request):  # to add or remove the items from the store
    try:
        shop = Store.objects.filter(merchant__user=request.user)[0]
    except:
        print("current user does not have any shops, return to the home page")
        return HttpResponseRedirect('/shopadmin')
    items = StoreItem.objects.filter(shop=shop).order_by('id')
    form = StoreItemForm(initial={'shop': shop})
    total_orders = Order.objects.filter(store=shop,status="Delivered").count()
    paginator = Paginator(items, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'form': form,'total_orders':total_orders,'rating':shop.rating}
    return render(request, 'inventory.html', context)


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
