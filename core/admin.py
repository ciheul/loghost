from django.contrib import admin

from core.models import City, Site, SiteType


admin.site.register(City)
admin.site.register(Site)
admin.site.register(SiteType)
