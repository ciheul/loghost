from django.contrib import admin

from core.models import Awb, City, GoodType, ItemStatus, PaymentType, Service, Site, SiteType


admin.site.register(Awb)
admin.site.register(City)
admin.site.register(GoodType)
admin.site.register(ItemStatus)
admin.site.register(PaymentType)
admin.site.register(Service)
admin.site.register(Site)
admin.site.register(SiteType)
