from django.conf.urls import url

from core import api, views


urlpatterns = [
    url(r'^dashboard/$', views.DashboardView.as_view(), name='core-dashboard'),
    url(r'^management/agent/$', views.AgentManagementView.as_view(), name='core-agent'),

    url(r'^api/agent/$', api.AgentReadApi.as_view(), name='api-agent-read'),
    url(r'^api/agent/create/$', api.AgentCreateApi.as_view(), name='api-agent-create'),
    url(r'^api/agent/update/$', api.AgentUpdateApi.as_view(), name='api-agent-update'),
    url(r'^api/agent/delete/$', api.AgentDeleteApi.as_view(), name='api-agent-delete'),
]
