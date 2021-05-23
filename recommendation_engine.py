import json,math,os
import django
import requests


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()
from store import models

#Address conversion to latitude and longitude

def get_lat_long(location):
    parameters = {
    "key" : "h0rGftGyPqqLqVZE0b0d1nzKnTAxpuMe",
    "location" : location
    }
    response = requests.get("http://www.mapquestapi.com/geocoding/v1/address",params=parameters)
    data = json.loads(response.text)['results']
    lat = data[0]['locations'][0]['latLng']['lat']
    lng = data[0]['locations'][0]['latLng']['lng']
    return lat,lng


#Distance Calculation between 2 points

R = 6373.0


def get_dist(lat1,lon1,lat2,lon2):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlon = lon2-lon1
    dlat = lat2-lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R*c

a,b = get_lat_long("Bits Pilani , Hyderabad, Telengana 500078")
c,d = get_lat_long("BE-21 Newtown Action Area 1B, Kolkata 700156")

#print(get_dist(a,b,c,d))


#Finding valid list of shops according to given range defined.
def get_valid_shops():
    prime_delivery=False
    range=0.7
    valid_shopkeepers = {}
    customer_lat = 17.41710876415962
    customer_long = 78.44529794540337
    shopkeeper_dataset = models.Store.objects.all()
    for shopkeeper in shopkeeper_dataset.iterator():
        distance = get_dist(customer_lat,customer_long,shopkeeper.lat,shopkeeper.long)
        if(distance<=range):
            valid_shopkeepers[shopkeeper.name] = distance
    if not valid_shopkeepers:
        prime_delivery=True                   # Found No STORE nearby. Fall back to amazon flex or amazon prime delivery
    #valid_shopkeepers = {k: v for k, v in sorted(valid_shopkeepers.items(), key=lambda item: item[1])}             For Sorted Values
    return prime_delivery,valid_shopkeepers

def ratings_prepocessor():
    rated_shopkeepers = {}
    shopkeeper_dataset = models.Store.objects.all()
    for shopkeeper in shopkeeper_dataset.iterator():
        rated_shopkeepers[shopkeeper.name] = shopkeeper.rating
    return rated_shopkeepers

def number_of_sucessful_orders():
    sucessful_orders = {}
    shopkeeper_dataset = models.Store.objects.all()
    for shopkeeper in shopkeeper_dataset.iterator():
        sucessful_orders[shopkeeper.name] = shopkeeper.total_orders
    return sucessful_orders

def recommendation_algo():
    # IF shop is not in range is ineligble move to prime delivery
    prime,shop_list = get_valid_shops()
    rated_shopkeepers = ratings_prepocessor()
    sucessful_orders = number_of_sucessful_orders()
    if(prime==True):
        return "Redirect to amazon warehouse for delivery via amazon flex or prime delivery."
    finalshoplist = {}
    for i,j in shop_list.items():
        val = j*0.40                            #Distance Calculation 40% weightage
        val += rated_shopkeepers[i]*0.20        #Ratings Calculation 20% weightage
        val += sucessful_orders[i]*0.40         #Succesful orders Calculation 40% weightage
        finalshoplist[i]=val
    finalshoplist = {k: v for k, v in sorted(finalshoplist.items(), key=lambda item: item[1],reverse=True)} 
    return finalshoplist

if __name__ == '__main__':
    from orders.models import Recommendations
    req_val = recommendation_algo()
    for i,j in req_val.items():
        query = Recommendations(shop=i,score=j)
        query.save()

