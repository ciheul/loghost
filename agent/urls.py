from django.conf.urls import url

from agent import views


urlpatterns = [
    url(r'^dashboard/$', views.DashboardView.as_view(), name='ag-dashboard'),
    url(r'^fill/$', views.FillView.as_view(), name='ag-fill'),
    url(r'^track/$', views.TrackView.as_view(), name='ag-track'),
    url(r'^tariff/$', views.TariffView.as_view(), name='ag-tariff'),
    url(r'^report/$', views.ReportView.as_view(), name='ag-report'),
    url(r'^shipment/$', views.ShipmentView.as_view(), name='ag-shipment'),
    url(r'^shipment/receipt$', views.ShipmentReceiptView.as_view(), name='ag-shipment-receipt'),
    url(r'^profile/$', views.ProfileView.as_view(), name='ag-profile'),
]
