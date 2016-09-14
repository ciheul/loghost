from django.contrib import admin

from core.models import City, Service, Site, SiteType


admin.site.register(City)
admin.site.register(Service)
admin.site.register(Site)
admin.site.register(SiteType)
