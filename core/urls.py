from django.conf.urls import url

from core import api, views


urlpatterns = [
    url(r'^dashboard/$', views.DashboardView.as_view(),
        name='core-dashboard'),
    url(r'^management/tariff/$', views.TariffManagementView.as_view(),
        name='core-tariff'),
    url(r'^management/agent/$', views.AgentManagementView.as_view(),
        name='core-agent'),
    url(r'^management/agent/(?P<site_pk>\d+)/user/$',
        views.UserManagementView.as_view(), name='core-user'),

    # API

    # AGENT
    url(r'^api/agent/$', api.AgentReadApi.as_view(), name='api-agent-read'),
    url(r'^api/agent/create/$', api.AgentCreateApi.as_view(),
        name='api-agent-create'),
    url(r'^api/agent/update/$', api.AgentUpdateApi.as_view(),
        name='api-agent-update'),
    url(r'^api/agent/delete/$', api.AgentDeleteApi.as_view(),
        name='api-agent-delete'),

    # USER
    url(r'^api/user/$', api.UserReadApi.as_view(),
        name='api-user-read'),
    url(r'^api/user/create$', api.UserCreateApi.as_view(),
        name='api-user-create'),
    url(r'^api/user/update$', api.UserUpdateApi.as_view(),
        name='api-user-update'),
    url(r'^api/user/delete$', api.UserDeleteApi.as_view(),
        name='api-user-delete'),

    # TARIFF
    url(r'^api/tariff/check/$', api.TariffCheckApi.as_view(),
        name='api-tariff-check'),
]
