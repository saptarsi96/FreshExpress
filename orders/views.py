from django.shortcuts import render, redirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import generic
from orders.forms import OrderForm, ReviewForm,OrderUpdateForm
from orders.models import Order, OrderItem, Review
from cart.cart import Cart
from django.db.models import Count
import store
from store.models import Product, Store
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from recommendation_engine import *
import subprocess
# Create your views here.
import recommendation_engine
from orders.models import Recommendations
import json
import math
import os
import django
import requests
from django.db.models import Max, Min
from store import models
from time import sleep

class CreateOrder(LoginRequiredMixin, generic.CreateView):
    form_class = OrderForm
    template_name = 'orders/place_order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        products = Product.objects.filter(pk__in=cart.cart.keys())
        cart_items = map(
            lambda p: {'product': p, 'quantity': cart.cart[str(p.id)]['quantity'], 'total': p.price*cart.cart[str(p.id)]['quantity']}, products)
        context['summary'] = cart_items
        return context

    def form_valid(self, form):
        cart = Cart(self.request)
        if len(cart) == 0:
            return redirect('cart:cart_details')
        order = form.save(commit=False)
        order.user = self.request.user
        store = Store.objects.get(id=660453821292455697)
        order.store = store
        order.total_price = cart.get_total_price()
        order.save()
        products = Product.objects.filter(id__in=cart.cart.keys())
        orderitems = []
        for i in products:
            q = cart.cart[str(i.id)]['quantity']
            orderitems.append(
                OrderItem(order=order, product=i, quantity=q, total=q*i.price))
        OrderItem.objects.bulk_create(orderitems)
        cart.clear()
        messages.success(self.request, 'Your order is successfully forwarded to FreshExpress Store .')
       # os.system('python3 recommendation_engine.py')
        return redirect('store:product_list')


class MyOrders(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created').annotate(total_items=Count('items'))


class OrderDetails(LoginRequiredMixin, generic.DetailView):
    model = Order
    context_object_name = 'order'
    template_name = 'orders/order_details.html'

    def get_queryset(self, **kwargs):
        objs = super().get_queryset(**kwargs)
        return objs.filter(user=self.request.user).prefetch_related('items', 'items__product')


class OrderInvoice(LoginRequiredMixin, generic.DetailView):
    model = Order
    context_object_name = 'order'
    template_name = 'orders/order_invoice.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related('items', 'items__product')

    def get_object(self, **kwargs):
        obj = super().get_object(**kwargs)
        if obj.user_id == self.request.user.id or self.request.user.is_superuser:
            return obj
        raise Http404


class Recommend(LoginRequiredMixin):
    def recommendation_algo(request, **kwargs):
        plid = kwargs['plid']
        result = recommendation_engine.recommendation_algo(plid, request)
        form = OrderUpdateForm()
        return render(request, 'orders/show_view.html', context={'result': result,'form':form})
       # print(output)


class OrderRating(LoginRequiredMixin, generic.DetailView):
    def add_review(request, **kwargs):
        order = get_object_or_404(Order, **kwargs)
        form = ReviewForm(request.POST)
        if form.is_valid():
            object = form.save(commit=False)
            object.order = order
            try:
                ob2=Review.objects.filter(order=order)[0]
                ob2.userrating=object.userrating
                ob2.save()
            except:    
                object.save()
            result = recommendation_engine.ratingupdater()
            print("inside views:" + str(result))
        else:
            print(form)
        return render(request, 'orders/order_list.html', {'order': order, 'form': form})


def UpdateOrder(request):
    form = OrderUpdateForm(request.POST)
    if form.is_valid():
        try:
            order = Order.objects.get(id=form.cleaned_data['oid'])
            shop = Store.objects.get(id=form.cleaned_data['sid'])
            order.store = shop
            order.status = "Pending"
            order.paid = True
            order.save()
            print("Store object updated successfully")
            messages.success(request, 'Your order is successfully placed.')
            cart = Cart(request)
            cart.clear()
        except:
            print("Error while updating the store..check logs")
    else:
        print("form is invalid")
    return redirect('store:product_list')
    
