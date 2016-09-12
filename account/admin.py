from django.contrib import admin

from account.models import CustomUser, Organization


admin.site.register(CustomUser)
admin.site.register(Organization)
