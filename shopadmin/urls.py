from django.urls import path
from . import views

app_name = 'shopadmin'
urlpatterns = [
    path('', views.index),
    path('store', views.storehome),
    path('inventory', views.inventoryhome),
    path('redirectstore', views.redirecthome),
    path('redirectinventory', views.redirectinventory),
]
