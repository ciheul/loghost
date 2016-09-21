from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class AwbCounter(models.Model):
    last_serial_number = models.IntegerField()


class City(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=20, unique=True)


class Tariff(models.Model):
    origin = models.ForeignKey(City, related_name='tariff_origin')
    destination = models.ForeignKey(City, related_name='tariff_destination')
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


class ItemStatus(models.Model):
    code = models.CharField(max_length=2, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
        return self.name

class AWB(models.Model):
    number = models.CharField(max_length=30,unique=True)
    status = models.ForeignKey('ItemStatus', null=True, blank=True)

    def __unicode__(self):
        return self.number


class Item(models.Model):
    user = models.ForeignKey('account.CustomUser', null=True, blank=True)
    awb = models.ForeignKey('AWB', null=True, blank=True)
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


# class Item(models.Model):
#     user = models.ForeignKey('account.CustomUser')
#     awb = models.CharField(max_length=20, unique=True)
#     sender_name = models.CharField(max_length=50)
#     sender_address = models.CharField(max_length=100)
#     sender_city= models.ForeignKey(City),
#     sender_zip_code = models.IntegerField(null=True, blank=True)
#     sender_phone = models.CharField(max_length=15)
#     receiver_name = models.CharField(max_length=50)
#     receiver_address = models.CharField(max_length=100)
#     receiver_city= models.ForeignKey(City),
#     receiver_zip_code = models.IntegerField(null=True, blank=True)
#     receiver_phone = models.CharField(max_length=15)
#     good_name = models.CharField(max_length=50, null=True, blank=True)
#     good_value = models.CharField(max_length=50, null=True, blank=True)
#     information = models.CharField(max_length=100, null=True, blank=True)
#     instruction = models.CharField(max_length=100, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __unicode__(self):
        return self.awb


class ItemMetric(models.Model):
    item = models.ForeignKey(Item)
    weight = models.FloatField()
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()


class History(models.Model):
    awb = models.ForeignKey('AWB')
    status = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.item.awb + ': ' + self.status


class ItemSite(models.Model):
    awb = models.ForeignKey('AWB', null=True, blank=True)
    site = models.ForeignKey('Site', null=True, blank=True)
    rack_id = models.CharField(max_length=5, null=True, blank=True)
    received_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    received_by = models.CharField(max_length=50, null=True, blank=True)
    sent_at = models.DateTimeField( null=True, blank=True)
    sent_by = models.CharField(max_length=50, null=True, blank=True)
    item_status= models.ForeignKey('ItemStatus', null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


    def __unicode__(self):
        return 'awb %s - site %s' %(self.awb, self.site)


class Shipment(models.Model):
    cost = models.IntegerField( null=True, blank=True)
    transportation = models.ForeignKey('Transportation', null=True, blank=True)
    sent_by = models.CharField(max_length=20, null=True, blank=True)
    sent_at = models.DateTimeField( null=True, blank=True)
    received_by = models.CharField(max_length=20, null=True, blank=True)
    received_at = models.DateTimeField( null=True, blank=True)
    origin = models.CharField(max_length=20, null=True, blank=True)
    origin_site= models.ForeignKey('Site', null=True, blank=True, 
                                    related_name='origin')
    destination = models.CharField(max_length=20, null=True, blank=True)
    destination_site= models.ForeignKey('Site', null=True, blank=True, 
                                    related_name='destination')
    smu = models.CharField(max_length=15, null=True, blank=True)
    

    def __unicode__(self):
        return 'transportation %s' %(self.transportation)


class Transportation(models.Model):
    identifier = models.CharField(max_length=20)
    transportation_type = models.ForeignKey('TransportationType')
    origin_city= models.ForeignKey('City', null=True, blank=True, 
                                    related_name='origin')
    destination= models.ForeignKey('City', null=True, blank=True, 
                                    related_name='destination')
    departed_at = models.DateTimeField( null=True, blank=True)
    arrived_at = models.DateTimeField( null=True, blank=True)
    base = models.CharField(max_length=20, null=True, blank=True)
    operator = models.CharField(max_length=50, null=True, blank=True)
    operator_phone = models.CharField(max_length=15, null=True, blank=True)
    capacity = models.CharField(max_length=2, null=True, blank=True)

    def __unicode__(self):
        return self.identifier
    

class TransportationType(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True)

    def __unicode__(self):
        return self.name


class ItemShipment(models.Model):
    awb = models.ForeignKey('AWB', null=True, blank=True)
    shipment = models.ForeignKey('Shipment', null=True, blank=True)
    item_shipment_status = models.ForeignKey('ItemStatus', null=True, 
                                                blank=True)
    def __unicode__(self):
        return 'item_id %s - shipment_id %s' %(self.awb, self.shipment_id)


class ItemBagShipment(models.Model):
    awb = models.ForeignKey('AWB', null=True, blank=True)
    shipment = models.ForeignKey('Shipment', null=True, blank=True)
    bag = models.ForeignKey('Bag', null=True, blank=True)

    def __unicode__(self):
        return 'bag_id %s - shipment_id %s' %(self.bag_id, self.shipment_id)


class Bag(models.Model):
    number = models.CharField(max_length=30)

    def __unicode__(self):
        return self.number


class BagItem(models.Model):
    bag = models.ForeignKey('Bag', null=True, blank=True)
    awb = models.ForeignKey('AWB', null=True, blank=True)


class Courier(models.Model):
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    transportation_type = models.ForeignKey('TransportationType')
    
    def __unicode__(self):
        return self.name


class Delivery(models.Model):
    awb = models.ForeignKey('AWB')
    courier = models.ForeignKey('Courier')
    forwarder = models.ForeignKey('Forwarder')
    status = models.ForeignKey('ItemStatus', null=True, blank=True)
    receiver_name = models.CharField(max_length=30, null=True, blank=True)
    receive_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Forwarder(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=5)
    address = models.CharField(max_length=50)
    phone = models.CharField(max_length=12)

    def __unicode__(self):
        return self.name

