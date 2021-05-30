from django.db import models
from django.conf import settings
from store.models import Product, Store
from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE


# Create your models here.

choices = (
    ('Requested', 'Requested'),
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered')
)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='orders', on_delete=models.CASCADE)
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name='reviews', default=0)
    address = models.CharField(max_length=150, blank=False, null=False)

    pin_code = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        choices=choices, max_length=10, default='Pending')
    total_price = models.FloatField(null=False, blank=False)
    rating = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Order {self.id}'

    def get_absolute_url(self):
        return reverse('orders:invoice', kwargs={'pk': self.pk})


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name='ordered', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total = models.FloatField(null=False, blank=False)

    def __str__(self):
        return f'Order Item {self.id}'


class Recommendations(models.Model):
    shop = models.TextField(null=False, blank=False)
    score = models.FloatField(null=False, blank=False)
    accepted = models.BooleanField(default=False)
    order_time = models.DateTimeField(auto_now=True)
    status = models.CharField(
        choices=choices, max_length=10, default='Pending')


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    order = models.ForeignKey(
        Order, related_name='reviews', on_delete=models.CASCADE)
    userrating = models.IntegerField(choices=RATING_CHOICES)


class AcceptedOrderItem(models.Model):
    shop = models.ForeignKey(Store, on_delete=models.CASCADE)
    orderitem = models.ForeignKey(OrderItem, on_delete=models.CASCADE)

class RejectedOrder(models.Model):
    shop = models.ForeignKey(Store, on_delete=models.CASCADE,default=0)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,default=0)

# class UserAddress(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     address = models.CharField(max_length=1000)
#     pincode = models.CharField(max_length=7)
#     city = models.CharField(max_length=255)
#     lat = models.FloatField()
#     long = models.FloatField()
