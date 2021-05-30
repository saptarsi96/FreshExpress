from django.db import models
from django.contrib.auth.models import User

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=1000)
    pincode = models.CharField(max_length=7)
    city = models.CharField(max_length=255)
    lat = models.FloatField(default=17.41710876415962)
    long = models.FloatField(default=78.44529794540337)