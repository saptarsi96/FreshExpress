from os import name
import shopadmin
from django.urls import path, include
from accounts import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register', views.Register.as_view(), name='register'),
    path('profile', views.profile, name='profile'),
    path('shopadmin/',include('shopadmin.urls',namespace='shopadmin')),
    path('address',views.changeAddress,name='address'),
    path('help',views.help,name="help")
]
