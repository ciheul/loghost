from django.contrib import admin

from core.models import Awb, City, GoodType, ItemSite, ItemShipment, ItemStatus, PaymentType, Service, Site, SiteType


admin.site.register(Awb)
admin.site.register(City)
admin.site.register(GoodType)
admin.site.register(ItemStatus)
admin.site.register(ItemShipment)
admin.site.register(ItemSite)
admin.site.register(PaymentType)
admin.site.register(Service)
admin.site.register(Site)
admin.site.register(SiteType)
