from django.urls import path
from . import views

app_name = 'shopadmin'
urlpatterns = [
    path('', views.index)
]
