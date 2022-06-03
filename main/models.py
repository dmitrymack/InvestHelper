from django.db import models
from django.contrib.auth.models import User


class Stock(models.Model):
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    dailyLow = models.DecimalField(max_digits=9, decimal_places=2)
    dailyHigh = models.DecimalField(max_digits=9, decimal_places=2)
    currency = models.CharField(max_length=5)
    cap = models.DecimalField(max_digits=15, decimal_places=2)


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True)


class Index(models.Model):
    indexTicker = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    currency = models.CharField(max_length=5)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    stock = models.ManyToManyField(Stock)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    stock = models.ManyToManyField(Stock)
    comment = models.TextField()
