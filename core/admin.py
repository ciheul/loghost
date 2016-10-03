from django.contrib import admin

from core.models import AwbCounter, AWB, City, GoodType, ItemSite, ItemShipment, ItemStatus, PaymentType, Service, Site, SiteType, Transportation, TransportationType, Courier, Bag, Forwarder

admin.site.register(AwbCounter)
admin.site.register(AWB)
admin.site.register(City)
admin.site.register(GoodType)
admin.site.register(ItemStatus)
admin.site.register(ItemShipment)
admin.site.register(ItemSite)
admin.site.register(PaymentType)
admin.site.register(Service)
admin.site.register(Site)
admin.site.register(SiteType)
admin.site.register(Transportation)
admin.site.register(TransportationType)
admin.site.register(Courier)
admin.site.register(Bag)
admin.site.register(Forwarder)
