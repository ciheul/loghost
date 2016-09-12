from django.conf.urls import url

from core import views


urlpatterns = [
    url(r'^dashboard/$', views.DashboardView.as_view(), name='core-dashboard'),

]
