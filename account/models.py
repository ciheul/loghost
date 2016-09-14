from __future__ import unicode_literals

from django.core.validators import validate_email
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.models import Site


class Organization(models.Model):
    name = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=50)
    province = models.CharField(max_length=30)
    zip_code = models.IntegerField()

    def __unicode__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser,
                     **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff,
                          is_active=True,
                          is_superuser=is_superuser,
                          last_login=timezone.now(),
                          date_joined=timezone.now(),
                          **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # username = models.CharField(_('username'), max_length=30, unique=True)
    fullname = models.CharField(_('full name'), max_length=100,
                                 null=True, blank=True)
    email = models.EmailField(_('email address'), max_length=254,
                              unique=True, validators=[validate_email])
    organization = models.ForeignKey(Organization, null=True, blank=True)
    site = models.ForeignKey(Site, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']

    # objects = UserManager()
    objects = CustomUserManager()

    # def create_user(self):
    def get_short_name(self):
        return self.fullname


# class CustomUserManager(BaseUserManager):
