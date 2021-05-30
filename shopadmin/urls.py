from os import name
from shopadmin.inventoryviews import redirectremoveitems
from django.urls import path
from . import views

app_name = 'shopadmin'
urlpatterns = [
    path('', views.index),
    path('store', views.storehome,name='store'),
    path('inventory', views.inventoryhome,name='inventory'),
    path('redirectstore', views.redirecthome,name='redirectstore'),
    path('redirectinventory', views.redirectinventory,name='redirectinventory'),
    path('redirectadditem', views.redirectadditems,name='redirectadditem'),
    path('redirectremoveitem', views.redirectremoveitems,name='redirectremoveitem'),
    path('receivedorders', views.ReceivedOrders,name='receivedorders'),
    path('redirectreceivedorders', views.RedirectReceivedOrders,name='redirectreceivedorders'),
    path('acceptedorders', views.AcceptedOrders,name='acceptedorders'),
]
