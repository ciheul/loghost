from django.conf.urls import url

from agent import views
from agent import api

urlpatterns = [
    url(r'^dashboard/$', views.DashboardView.as_view(), name='ag-dashboard'),
    url(r'^fill/$', views.FillView.as_view(), name='ag-fill'),
    url(r'^fill/multiple/$', views.FillMultipleView.as_view(), name='ag-fill-multiple'),
    url(r'^track/$', views.TrackView.as_view(), name='ag-track'),
    url(r'^tariff/$', views.TariffView.as_view(), name='ag-tariff'),
    url(r'^report/$', views.InventoryListView.as_view(), name='ag-report'),
    # url(r'^shipment/$', views.ShipmentView.as_view(), name='ag-shipment'),
    # url(r'^shipment/receipt$', views.ShipmentReceiptView.as_view(), name='ag-shipment-receipt'),
    url(r'^profile/$', views.ProfileView.as_view(), name='ag-profile'),
    # url(r'^new/report/$', views.NewReportView.as_view(), name='ag-newreport'),
    url(r'^blank/report/$', views.BlankReportView.as_view(), name='ag-blank'),
    url(r'^delivery/report/$', views.DeliveryReportView.as_view(), name='ag-delivery'),
    url(r'^manifest/report/$', views.ManifestReportView.as_view(), name='ag-manifest'),

    # PRINT
    url(r'^fill/consigment/print/(?P<item_id>\d+)/$', views.ReportView.as_view(), name='ag-print-shipment-detail'),
    url(r'^fill/consigment/multiple/print/(?P<item_id>.+)/$', views.ReportMultipleView.as_view(), name='ag-print-shipment-detail-multiple'),
    url(r'^shipment/marking/(?P<item_id>\d+)/$', views.ShipmentMarkingView.as_view(), name='ag-shipment-marking'),

    # API
    url(r'^api/agent/item/create/$', api.AgentItemCreateApi.as_view(), name='api-agent-item-create'),
    url(r'^api/agent/item/create/multi/$', api.AgentItemCreateMultiApi.as_view(), name='api-agent-item-create-multi'),
]
