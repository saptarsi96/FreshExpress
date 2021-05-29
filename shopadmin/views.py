from django.db.models.query import FlatValuesListIterable
from django.http.response import HttpResponse
from django.shortcuts import render
from orders.models import Order, OrderItem,AcceptedOrderItem,RejectedOrder
from store.models import Product
from .inventoryviews import *
from django.views.generic.list import ListView
from django.core.paginator import Paginator
from django.forms import formset_factory
from .inventoryforms import OrderItemForm,DeliveredForm
import smtplib, ssl
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
def AcceptedOrders(request):
    try:
        shop = Store.objects.filter(merchant__user=request.user)[0]
    except:
        print("current user does not have any shops, return to the home page")
        return HttpResponseRedirect('/shopadmin')
    #fetch the orders from the orders whose status is Accepted  (change it to new)
    form = DeliveredForm(request.POST)
    if form.is_valid():
        try:
            order = Order.objects.get(pk=form.cleaned_data['order'])
            order.status = "Delivered"
            order.save()
        except:
            print("current order does not exist")
    else:
        print("form is invalid")

    orders = Order.objects.filter(store=shop,status="Accepted")
    print(orders)
    allorderslist = []
    for order in orders:
        orderlist = {}
        orderitems = AcceptedOrderItem.objects.filter(shop=shop,orderitem__order=order)
        if(len(orderitems)!=0):
            orderlist['order'] = order
            orderlist['items'] = orderitems
            allorderslist.append(orderlist)
    print(allorderslist)
    paginator = Paginator(allorderslist, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj':page_obj}
    return render(request, 'current_orders.html', context)


@login_required
def ReceivedOrders(request):
    # fetch the orders which are releavnt to the current shop
    try:
        shop = Store.objects.filter(merchant__user=request.user)[0]
    except:
        print("current user does not have any shops, return to the home page")
        return HttpResponseRedirect('/shopadmin')
    #get the list of the orders which are already worked on 
    accepted = AcceptedOrderItem.objects.filter(shop=shop).values_list('orderitem__order__id').distinct()
    rejected = RejectedOrder.objects.filter(shop=shop).values_list('order__id')
    #get the valid orders for the shop
    allorders = Order.objects.filter(status="Pending").exclude(pk__in=accepted).exclude(pk__in=rejected)
    orderlist = []
    #fetcht the items present for the current owner
    present = StoreItem.objects.filter(shop=shop,status=True).values_list('product__id',flat=True)
    for order in allorders:
        # only fetch the items which are available to the shopkeeper
        li = OrderItem.objects.filter(order=order,product__id__in=present).values('product__name', 'id','order__id','product__id')
        if(len(list(li))!=0):
            idlist = li.values('id')
            li = list(li)
            orderlist.append(li)
    paginator = Paginator(orderlist, 8)
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
                r= RejectedOrder(order= orderob,shop=shop)
                r.save()
            except:
                print("error while inserting rejected order")
    else:
        print("form is invalid")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def support(request):
    return render(request,'support.html')
def send(username,email,queries):
    email_id="guptahimanshu2035@gmail.com"
    password="ajyfgrezutgkypdd"
    try:
        subject ="""\
        Support FreshEXpress
        """
        text="""\
        Hello {0},
        we have received your query regarding"{1}".Our Agent  will contact you soon 
        Thankyou
        Stay safe and stay connected """.format(username,queries)
        conn=smtplib.SMTP('imap.gmail.com',587)
        conn.ehlo()
        conn.starttls()
        conn.login(email_id,password)
        message = 'Subject: {}\n\n{}'.format(subject, text)
        conn.sendmail(email_id,email,message)
        return 1
    except KeyError:
        return 0
def help(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        queries=request.POST.get('queries')
        result=send(username,email,queries)
        if result==1:
            return HttpResponse("Mail is sent") 
        else:
            return HttpResponse("Mail is not sent") 