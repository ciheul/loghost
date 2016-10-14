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
    url(r'^management/bagging/list/$', views.BaggingListManagementView.as_view(), name='core-bagging-list'),
    url(r'^management/bagging/list/(?P<bag_id>\d+)/item/$',
        views.BaggingItemManagementView.as_view(), name='core-bagging-list-item'),
    url(r'^management/consigment/$', views.ConsignmentNoteManagementView.as_view(),
        name='core-consigment'),
    url(r'^management/consigment/multiple/$', views.ConsignmentNoteMultiManagementView.as_view(), name='core-consigment-multiple'),
    url(r'^management/manifest/$', views.ManifestingManagementView.as_view(),
        name='core-manifest'),
    url(r'^management/manifestinglist/$', views.ManifestingListView.as_view(), name='core-manifestinglist'),
    url(r'^management/airport/$', views.AirportManagementView.as_view(),
        name='core-airport'),
    url(r'^management/airportlist/$', views.AirportListView.as_view(), name='core-airportlist'),
    url(r'^management/arrival/$', views.ArrivalManagementView.as_view(),
        name='core-arrival'),
    url(r'^management/arrivalbag/$', views.ArrivalBagManagementView.as_view(),
        name='core-arrival-bag'),
    url(r'^management/arrivalitem/$', views.ArrivalItemManagementView.as_view(),
        name='core-arrival-item'),
    url(r'^management/delivery/$', views.DeliveryManagementView.as_view(),
        name='core-delivery'),
    url(r'^management/deliveryforward/$', views.DeliveryThirdPartyManagementView.as_view(),
        name='core-delivery-third'),
    url(r'^management/deliveryupdate/$', views.DeliveryUpdateManagementView.as_view(),
        name='core-delivery-update'),
    url(r'^management/inventory/$', views.InventoryManagementView.as_view(),
        name='core-inventory'),
    url(r'^management/transportation/$', views.TransportationManagementView.as_view(), name='core-transportation'),
    url(r'^management/courier/$', views.CourierManagementView.as_view(), name='core-courier'), 
    
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
    url(r'^api/bagging/list/$', api.BaggingListApi.as_view(), name='api-bagging-list'),
    url(r'^api/bagging/list/item/$', api.BaggingListItemApi.as_view(), name='api-bagging-list-item'),
    url(r'^api/onprocess/$',api.ItemOnProcess.as_view(), 
        name='api-onprocess'),
    url(r'^api/delivery/create/$',api.ItemDeliveryCreateApi.as_view(), 
        name='api-delivery-create'),
    url(r'^api/delivery/update/$',api.ItemDeliveryUpdateApi.as_view(), 
        name='api-delivery-update'),

    # TRANSPORTATION
    url(r'api/transportation/$', api.TransportationReadApi.as_view(), name='api-transportation-read'),
    url(r'^api/transportation/create/$', api.TransportationCreateApi.as_view(), name='api-transportation-create'),
    url(r'^api/transportation/update/$', api.TransportationUpdateApi.as_view(), name='api-transportation-update'),
    url(r'^api/transportation/delete/$', api.TransportationDeleteApi.as_view(), name='api-transportation-delete'),

    # COURIER
    url(r'api/courier/$', api.CourierReadApi.as_view(), name='api-courier-read'),
    url(r'api/courier/create/$', api.CourierCreateApi.as_view(), name='api-courier-create'), 
    url(r'^api/courier/update/$', api.CourierUpdateApi.as_view(), name='api-courier-update'),
    url(r'^api/courier/delete/$', api.CourierDeleteApi.as_view(), name='api-courier-delete'),

    # BAG
    url(r'api/bag/create/$', api.BagCreateApi.as_view(), name='api-bag-create'), 
    url(r'^api/bag/update/$', api.BagUpdateApi.as_view(), name='api-bag-update'),
    url(r'^api/bag/delete/$', api.BagDeleteApi.as_view(), name='api-bag-delete'),


    # TARIFF
    url(r'^api/tariff/$', api.TariffReadApi.as_view(),
        name='api-tariff-read'),
    url(r'^api/tariff/create/$', api.TariffCreateApi.as_view(),
        name='api-tariff-create'),
    url(r'^api/tariff/update/$', api.TariffUpdateApi.as_view(),
        name='api-tariff-update'),
    url(r'^api/tariff/delete/$', api.TariffDeleteApi.as_view(),
        name='api-tariff-delete'),
    url(r'^api/tariff/check/$', api.TariffCheckApi.as_view(),
        name='api-tariff-check'),

    # AGENT
    url(r'^api/agent/$', api.AgentReadApi.as_view(),
        name='api-agent-read'),
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
    url(r'^api/item/create/$', api.ItemCreateApi.as_view(),
        name='api-item-create'),
    url(r'^api/item/create/multi/$', api.ItemCreateMultiApi.as_view(), name='api-item-create-multi'),
    url(r'^api/item/track/$', api.ItemTrackApi.as_view(),
        name='api-item-track'),
    url(r'^api/item/site/(?P<site_pk>\d+)/$', api.ItemSiteApi.as_view(),
        name='api-item-site'),

    # PICK UP
    url(r'^api/site/pickup/', api.PickUpReadApi.as_view(), name='api-pickup-read'),

    # SHIPMENT
    url(r'^api/shipment/manifestlist/$', api.ManifestingListApi.as_view(), name='api-manifesting-list'),

    # UP LIFTING
    url(r'^api/uplifting/airportlist/$', api.AirportListApi.as_view(), name='api-airport-list'),
    
    # PRINT
    url(r'^management/manifestinglist/print/(?P<shipment_pk>\d+)/$',views.PrintManifestView.as_view(), name='print-manifest-form'),
    url(r'^management/consigment/print/(?P<item_id>\d+)/$', views.PrintFilledShipmentDetailView.as_view(), name='print-shipment-detail-form'),
    url(r'^management/consigment/multiple/print/(?P<item_id>.+)/$', views.PrintMultipleFilledShipmentDetailView.as_view(), name='print-shipment-detail-form-multiple'),
    url(r'^shipment/marking/(?P<item_id>\d+)/$', views.ShipmentMarkingView.as_view(), name='core-shipment-marking'),
]
