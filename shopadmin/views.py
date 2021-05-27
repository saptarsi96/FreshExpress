from django.http.response import HttpResponse
from django.shortcuts import render
from orders.models import Order, OrderItem, RejectionReason, AcceptedOrderItem
from store.models import Product
from .inventoryviews import *
from django.views.generic.list import ListView
from django.core.paginator import Paginator
from django.forms import formset_factory
from .inventoryforms import OrderItemForm
# Create your views here.


def index(request):
    orderlist = {}
    allorders = Order.objects.all()
    for singleorder in allorders:
        li = list(OrderItem.objects.filter(
            order=singleorder).values_list('product__name', flat=True))
        orderlist[singleorder.id] = li
    context = {'li': orderlist}
    return render(request, 'index4.html', context)


class OrdersList(ListView):
    paginate_by = 5
    queryset = Order.objects.prefetch_related('id').all()
    context_object_name = 'Orderlist'


@login_required
def ReceivedOrders(request):
    # fetch the orders which are releavnt to the current shop
    try:
        shop = Store.objects.filter(merchant__user=request.user)[0]
    except:
        print("current user does not have any shops, return to the home page")
        return HttpResponseRedirect('/shopadmin')
    #get the valid orders for the shop
    allorders = Order.objects.all()
    orderlist = []
    # fetcht the items present for the current owner
    present = [3]
    for order in allorders:
        li = OrderItem.objects.filter(order=order).values(
            'product__name', 'id', 'order__id', 'product__id')
        idlist = li.values('id')
        li = list(li)
        orderlist.append(li)
    paginator = Paginator(orderlist, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'present': present}
    return render(request, 'received.html', context)


@login_required
def RedirectReceivedOrders(request):
    form = OrderItemForm(request.POST)
    try:
        shop = Store.objects.filter(merchant__user=request.user)[0]
    except:
        print("current user does not have any shops, return to the previous page")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if form.is_valid():
        # if request is accepted by the store owner
        if('Accept' in request.POST):
            # fetch the orderitems of the selected orders
            items = form.cleaned_data['orderitems']
            orderitems = items.split('_')
            # if no values are accepted return
            if(items == ""):
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            items = OrderItem.objects.filter(pk__in=orderitems)
            for item in items:
                ob = AcceptedOrderItem(shop=shop, orderitem=item)
                ob.save()
            # store the given order items in the db
        else:
            try:
                orderid = form.cleaned_data['orderid']
                orderob = Order.objects.get(id=orderid)
                print(orderob)
                reason = "Rejcted"
                r = RejectionReason(orderid=orderob, reason=reason, shop=shop)
                r.save()
            except:
                print("error")
    else:
        print("form is invalid")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))