from orders.forms import OrderUpdateForm
from django.urls import path
from orders import views
app_name = 'orders'
urlpatterns = [
    path('place/<int:sid>/<int:oid>', views.CreateOrder.as_view(), name='place'),
    path('recommend/<str:plid>',
         views.Recommend.recommendation_algo, name='recommend'),
    path('my', views.MyOrders.as_view(), name='my'),
    path('details/<int:pk>/', views.OrderDetails.as_view(), name='details'),
    path('invoice/<int:pk>/', views.OrderInvoice.as_view(), name='invoice'),
    path('rating/<int:pk>', views.OrderRating.add_review, name='rating'),
    path('redirectupdateorder',views.UpdateOrder)
]
