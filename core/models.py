from __future__ import unicode_literals

from django.db import models


class City(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name


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
