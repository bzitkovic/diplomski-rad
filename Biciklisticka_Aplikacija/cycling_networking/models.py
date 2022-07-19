from django.db import models
from django.contrib.auth.models import AbstractUser
from .countries import getCountries


class User(AbstractUser):
    countrNames = getCountries()
    name = models.CharField(max_length=200, null=True)
    username = models.CharField(unique=True, max_length=50, null=False)
    email = models.EmailField(null=False)
    bio = models.TextField(null=True, max_length=500)
    country = models.CharField(null=False, max_length=25, choices=countrNames, default=("HR"))
    avatar = models.ImageField(null=True, upload_to="avatars")

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [username, email]


class Ride(models.Model):
    title = models.CharField(max_length=200, null=False)
    start_latitude = models.FloatField(null=False)
    start_longitude = models.FloatField(null=False)
    end_latitude = models.FloatField(null=False)
    end_longitude = models.FloatField(null=False)
    description = models.TextField(null=True, max_length=500)
    ride_date = models.DateField(null=True)
    ride_image = models.ImageField(null=True, upload_to="ride_images")
    cyclist = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Event(models.Model):
    name = models.CharField(max_length=50, null=False)
    city = models.CharField(max_length=50, null=False)
    date = models.DateTimeField(null=False)
    entry_fee = models.IntegerField(null=False)
    url = models.CharField(max_length=255, null=True)
    start_latitude = models.FloatField(null=False)
    start_longitude = models.FloatField(null=False)
    end_latitude = models.FloatField(null=False)
    end_longitude = models.FloatField(null=False)
    cyclist = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
