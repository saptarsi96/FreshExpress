from shopadmin.inventoryviews import redirectremoveitems
from django.urls import path
from . import views

app_name = 'shopadmin'
urlpatterns = [
    path('', views.index),
    path('store', views.storehome),
    path('inventory/<int:storeid>', views.inventoryhome),
    path('redirectstore', views.redirecthome),
    path('redirectinventory', views.redirectinventory),
    path('redirectadditem', views.redirectadditems),
    path('redirectremoveitem', views.redirectremoveitems),
    path('receivedorders', views.ReceivedOrders),
    path('redirectreceivedorders', views.RedirectReceivedOrders),
]
