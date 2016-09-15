from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Awb(models.Model):
    last_serial_number = models.IntegerField()


class City(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=20, unique=True)


class Tariff(models.Model):
    origin = models.ForeignKey(City, related_name='origin')
    destination = models.ForeignKey(City, related_name='destination')
    service = models.ForeignKey(Service)
    price = models.IntegerField()
    duration = models.CharField(max_length=10)

    class Meta:
        unique_together = ('origin', 'destination', 'service')


class SiteType(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name


class Site(models.Model):
    name = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=100)
    city = models.ForeignKey(City, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    zip_code = models.IntegerField(null=True, blank=True)
    type = models.ForeignKey(SiteType, null=True, blank=True)

    def __unicode__(self):
        return self.name


class PaymentType(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name


class GoodType(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name


class Item(models.Model):
    user = models.ForeignKey('account.CustomUser')
    awb = models.CharField(max_length=30, unique=True)
    sender_name = models.CharField(max_length=50)
    sender_address = models.CharField(max_length=100)
    sender_city = models.ForeignKey(City, related_name='sender_city')
    sender_zip_code = models.IntegerField(null=True, blank=True)
    sender_phone = models.CharField(max_length=15, null=True, blank=True)
    receiver_name = models.CharField(max_length=50)
    receiver_address = models.CharField(max_length=100)
    receiver_city = models.ForeignKey(City, related_name='receiver_city')
    receiver_zip_code = models.IntegerField(null=True, blank=True)
    receiver_phone = models.CharField(max_length=15, null=True, blank=True)
    payment_type = models.ForeignKey(PaymentType)
    good_name = models.CharField(max_length=50, null=True, blank=True)
    good_value = models.IntegerField(null=True, blank=True)
    good_type = models.ForeignKey(GoodType)
    quantity = models.IntegerField()
    weight = models.FloatField(null=True, blank=True)
    length = models.FloatField(null=True, blank=True)
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    information = models.CharField(max_length=200, null=True, blank=True)
    instruction = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    tariff = models.ForeignKey(Tariff)

    def __unicode__(self):
        return self.awb


class ItemMetric(models.Model):
    item = models.ForeignKey(Item)
    weight = models.FloatField()
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()


class History(models.Model):
    item = models.ForeignKey(Item)
    status = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.item.awb + ': ' + self.status
