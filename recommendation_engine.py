from store.models import StoreItem
from store.models import Product, Store
from orders import models as orderdb
from store import models
import json
import math
import os
import django
import requests
from django.db.models import Max, Min
from orders.models import AcceptedOrderItem
import store
from orders.forms import OrderForm
from orders.models import Order,OrderItem
from django.shortcuts import render, redirect, Http404, HttpResponse
from cart.cart import Cart
from django.contrib import messages
from time import sleep
from accounts.models import UserAddress

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()
# todoAddress conversion to latitude and longitude


def get_lat_long(location):
    parameters = {
        "key": "h0rGftGyPqqLqVZE0b0d1nzKnTAxpuMe",
        "location": location
    }
    response = requests.get(
        "http://www.mapquestapi.com/geocoding/v1/address",
        params=parameters)
    data = json.loads(response.text)['results']
    lat = data[0]['locations'][0]['latLng']['lat']
    lng = data[0]['locations'][0]['latLng']['lng']
    return lat, lng


#!Distance Calculation between 2 points

R = 6373.0


def get_dist(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


a, b = get_lat_long("Bits Pilani , Hyderabad, Telengana 500078")
c, d = get_lat_long("BE-21 Newtown Action Area 1B, Kolkata 700156")

# print(get_dist(a,b,c,d))


# Finding valid list of shops according to given range defined.
def get_valid_shops(order_id_cart):
    prime_delivery = False
    range = 2
    valid_shopkeepers = {}
    customer_lat = 17.41710876415962
    customer_long = 78.44529794540337
    shopkeeper_dataset = models.Store.objects.all().filter(shop_status='Open')
    ##########################################
    accepted_shoplist=set()
    accepted_dataset=AcceptedOrderItem.objects.all().filter(orderitem__order__id=order_id_cart)
    #print(accepted_dataset[0].shop_id)
    for i in accepted_dataset:
        accepted_shoplist.add(i.shop_id)
    #print("Accepting Shoplist")    
    #print(accepted_shoplist)
    #####################################3
    for shopkeeper in shopkeeper_dataset.iterator():
        distance = get_dist(
            customer_lat,
            customer_long,
            shopkeeper.lat,
            shopkeeper.long)
        if(distance <= range):
            if(shopkeeper.id in accepted_shoplist):
                valid_shopkeepers[shopkeeper.name] = [distance, shopkeeper.id]
           # print(valid_shopkeepers[shopkeeper.name])
    if not valid_shopkeepers:
        # Found No STORE nearby. Fall back to amazon flex or amazon prime
        # delivery
        prime_delivery = True
    # valid_shopkeepers = {k: v for k, v in sorted(valid_shopkeepers.items(),
    # key=lambda item: item[1])}             For Sorted Values
   # print("validshops")
    #print(valid_shopkeepers)
    return prime_delivery, valid_shopkeepers


def valid_shops_items():
    prime_delivery = False
    range = 2
    valid_shops = []
    customer_lat = 17.41710876415962
    customer_long = 78.44529794540337
    shopkeeper_dataset = models.Store.objects.all().filter(shop_status='Open')
    for shopkeeper in shopkeeper_dataset.iterator():
        distance = get_dist(
            customer_lat,
            customer_long,
            shopkeeper.lat,
            shopkeeper.long)
        if(distance <= range):
            valid_shops.append(shopkeeper)
    return valid_shops


def ratings_prepocessor():
    rated_shopkeepers = {}
    shopkeeper_dataset = models.Store.objects.all()
    for shopkeeper in shopkeeper_dataset.iterator():
        rated_shopkeepers[shopkeeper.name] = shopkeeper.rating
    upper_range = models.Store.objects.all().aggregate(
        Max('rating'))                   # To calculate max value for that column
    lower_range = models.Store.objects.all().aggregate(
        Min('rating'))                   # To calculate min value for that column
    return rated_shopkeepers, upper_range['rating__max'], lower_range['rating__min']


def number_of_sucessful_orders():
    sucessful_orders = {}
    shopkeeper_dataset = models.Store.objects.all()
    for shopkeeper in shopkeeper_dataset.iterator():
        sucessful_orders[shopkeeper.name] = shopkeeper.total_orders
    upper_range = models.Store.objects.all().aggregate(Max('total_orders'))
    lower_range = models.Store.objects.all().aggregate(Min('total_orders'))
    return sucessful_orders, upper_range['total_orders__max'], lower_range['total_orders__min']


def scaling(OldMax, OldMin, NewMax, NewMin, OldValue):
    OldRange = (OldMax - OldMin)
    NewRange = (NewMax - NewMin)
    NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
    return NewValue


def ratingupdater():
    review_dataset = orderdb.Review.objects.all().order_by(
        '-order_id')[:1]  # Get the most recent element of a order
    for reviews in review_dataset.iterator():
        order_entity = orderdb.Order.objects.get(id=reviews.order_id)
        store_entity_orders_table = order_entity.store_id

        store_entity_stores_table = models.Store.objects.get(
            id=store_entity_orders_table)
        prev_val = store_entity_stores_table.rating * \
            store_entity_stores_table.total_orders  # Prev Rating
        prev_val += reviews.userrating  # Updated Rating
        new_val = prev_val / (store_entity_stores_table.total_orders + 1)
       # print(round(new_val))
        store_entity_stores_table.rating = new_val
        store_entity_stores_table.total_orders = store_entity_stores_table.total_orders + 1
        store_entity_stores_table.save()
        # if reviews.order_id == orderdb.Order.objects.all().filter('order_id'):
        #     print(orderdb.Order.objects.all().filter('store'))
        # print(reviews.order_id,reviews.userrating)


def recommendation_algo(plid, request):
    # Create the order and orderitems for the 
    
    cart = Cart(request)
    print(vars(cart))
    if len(cart) == 0:
        return redirect('cart:cart_details')
    if(cart.getorder()=="NULL"):
        try:
            addr2 = UserAddress.objects.filter(user=request.user)[0]
            usercity = addr2.city 
            userpincode = addr2.pincode
            useraddress = addr2.address
        except:
            usercity = "Telangana"
            userpincode = "50078"
            useraddress = "BPHC Campus"
        order = Order(city=usercity,pin_code=userpincode,address=useraddress)
        #print("printing order id:")
        #print(order.id)
        order.user = request.user
        store = Store.objects.get(name='Admin',merchant__user__username='admin')
        order.store = store
        order.total_price = cart.get_total_price()
        order.status = "Requested"
        order.save()
        order_id_cart=order.id
        cart.addorder(order.id)
        products = Product.objects.filter(id__in=cart.cart.keys())
        orderitems = []
        for i in products:
            q = cart.cart[str(i.id)]['quantity']
            orderitems.append(
            OrderItem(order=order, product=i, quantity=q, total=q*i.price))
        OrderItem.objects.bulk_create(orderitems)
    else:
        order_id_cart=cart.getorder()
        order=Order.objects.get(id=order_id_cart)    
    #print("Order is created")
    sleep(15)
    #cart.clear()
    # IF shop is not in range is ineligble move to prime delivery
    #print("coming here")
    prime, shop_list = get_valid_shops(order_id_cart)
    # 3
    plid = plid.split(' ')
    productid = [int(i) for i in plid]
    result = {}
    from store.models import StoreItem
    shopnumber = valid_shops_items()
    # print(shopnumber)
    for i in range(0, len(shopnumber)):
        q = shopnumber[i].id
        si_query = StoreItem.objects.all().filter(shop=q).values('product', 'status')
        if(len(si_query) > 0):
            count = 0
            for k in range(0, len(si_query)):
                for j in range(0, len(productid)):
                    if(si_query[k]['product'] == productid[j]):
                        if(si_query[k]['status']) == True:
                            count += 1
            result[q] = count
    #print(result)
    ######################################################
    rated_shopkeepers, upper_shopkeeper, lower_shopkeeper = ratings_prepocessor()
    sucessful_orders, upper_successful_orders, lower_successful_orders = number_of_sucessful_orders()
    if(prime):
        return "Redirect to amazon warehouse for delivery via amazon flex or prime delivery."
    finalshoplist = {}
    for i, j in shop_list.items():
        # Distance Calculation 40% weightage   (*2.5 to scale since range is
        # defined at 2 KMS)
        val = j[0] * 0.40 * 2.5
        adder1 = scaling(upper_shopkeeper, lower_shopkeeper,
                         5, 0, rated_shopkeepers[i])  # Scaled
        val += adder1 * 0.20  # Ratings Calculation 20% weightage
        adder2 = scaling(
            upper_successful_orders,
            lower_successful_orders,
            5,
            0,
            sucessful_orders[i])
        val += adder2 * 0.20  # Succesful orders Calculation 20% weightage
        val = round(val, 1)
        finalshoplist[i] = [val, j[1]]

    ###########################################
    for k, v in finalshoplist.items():
        for key, value in result.items():
            if(v[1] == key):
                v.append(value)
                v.append(len(plid))
                v.append(order_id_cart)
                adder3 = value/len(plid)
                # Total number of orders deliverable 20% weightage and range scaling to 5
                v[0] += adder3 * 0.20 * 5
                v[0] = round(v[0], 1)
            else:
                pass
    print(finalshoplist)
    # print(finalshoplist[i])
    finalshoplist = {
        k: v for k,
        v in sorted(
            finalshoplist.items(),
            key=lambda item: item[1],
            reverse=True)}
    #print(finalshoplist)
    return finalshoplist