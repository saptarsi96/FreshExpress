import json,math
import requests

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

print(get_dist(a,b,c,d))


#Finding valid list of shops according to given range defined.

range=5

