from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, SET_NULL
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.


class Category(models.Model):
    name = models.TextField(max_length=50, null=False, blank=False)
    slug = models.SlugField(unique=True, max_length=100, db_index=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_absolute_path(self):
        return reverse('store:product_list') + f'?category={self.id}'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products')
    name = models.TextField(max_length=100, null=False, blank=False)
    slug = models.SlugField(unique_for_date='created')
    description = models.TextField(null=False, blank=False)
    price = models.FloatField(null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='media/products/%Y/%m/%d/', blank=True)
    availibility = models.BooleanField(null=False, default=True)

    class Meta:
        index_together = ('id', 'slug')
        ordering = ('-created',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_details', kwargs={'slug': self.slug})


class Merchant(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    joindate = models.DateField()


choices = (
    ('Open', 'Open'),
    ('Closed', 'Closed')
)


class Store(models.Model):
    name = models.CharField(max_length=1000)
    address = models.CharField(max_length=1000)
    contact = models.CharField(max_length=13)
    lat = models.FloatField()
    long = models.FloatField()
    start = models.TimeField()
    end = models.TimeField()
    gst = models.CharField(max_length=1000)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    shop_status = models.CharField(
        choices=choices, max_length=10, default='Open')


class StoreItem(models.Model):
    shop = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)


class UserGeoLocation(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE)
    latitude = models.FloatField(blank=False, null=False)
    longitude = models.FloatField(blank=False, null=False)
