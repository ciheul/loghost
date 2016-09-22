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
    url(r'^management/pickup/$', views.PickUpManagementView.as_view(),
        name='core-pickup'),
    url(r'^management/manualscan/$', views.ManualScanManagementView.as_view(),
        name='core-manualscan'),
    url(r'^management/bagging/$', views.BaggingManagementView.as_view(),
        name='core-bagging'),
    url(r'^management/consigment/$', views.ConsignmentNoteManagementView.as_view(),
        name='core-consigment'),
    url(r'^management/manifest/$', views.ManifestingManagementView.as_view(),
        name='core-manifest'),

    # API
    url(r'^api/item/insert/$',api.ItemInsertApi.as_view(), 
        name='api-item-insert'),
    url(r'^api/item/incident/$',api.ItemIncidentApi.as_view(), 
        name='api-item-incident'),
    url(r'^api/runsheet/create/$',api.RunsheetCreateApi.as_view(), 
        name='api-runsheet-create'),
    url(r'^api/runsheet/update/$',api.RunsheetUpdateApi.as_view(), 
        name='api-runsheet-update'),
    url(r'^api/outbound/$',api.OutboundApi.as_view(), 
        name='api-outbound'),
    url(r'^api/inbound/$',api.InboundApi.as_view(), 
        name='api-inbound'),
    url(r'^api/bagging/$',api.BaggingApi.as_view(), 
        name='api-bagging'),
    url(r'^api/onprocess/$',api.ItemOnProcess.as_view(), 
        name='api-onprocess'),
    url(r'^api/delivery/create/$',api.ItemDeliveryCreateApi.as_view(), 
        name='api-delivery-create'),
    url(r'^api/delivery/update/$',api.ItemDeliveryUpdateApi.as_view(), 
        name='api-delivery-update'),
    url(r'^api/delivery/failupdate/$',api.ItemDeliveryUpdateFailApi.as_view(), 
        name='api-delivery-failupdate'),



    # TARIFF
    url(r'^api/tariff/$', api.TariffReadApi.as_view(), name='api-tariff-read'),
    url(r'^api/tariff/create/$', api.TariffCreateApi.as_view(),
        name='api-tariff-create'),
    url(r'^api/tariff/update/$', api.TariffUpdateApi.as_view(),
        name='api-tariff-update'),
    url(r'^api/tariff/delete/$', api.TariffDeleteApi.as_view(),
        name='api-tariff-delete'),
    url(r'^api/tariff/check/$', api.TariffCheckApi.as_view(),
        name='api-tariff-check'),

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
    url(r'^api/user/create/$', api.UserCreateApi.as_view(),
        name='api-user-create'),
    url(r'^api/user/update/$', api.UserUpdateApi.as_view(),
        name='api-user-update'),
    url(r'^api/user/delete/$', api.UserDeleteApi.as_view(),
        name='api-user-delete'),

    # ITEM
    url(r'^api/item/create/$', api.ItemCreateApi.as_view(), name='api-item-create'),
    url(r'^api/item/track/$', api.ItemTrackApi.as_view(), name='api-item-track'),

    url(r'^api/item/site/(?P<site_pk>\d+)/$', api.ItemSiteApi.as_view(),
        name='api-item-site'),

    # PICK UP

]
