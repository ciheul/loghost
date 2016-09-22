from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View

from core.models import City, AWB, Service, Site, ItemStatus, ItemSite, SiteType, GoodType, PaymentType
from core.models import Transportation, TransportationType, Courier, Forwarder

class StaffView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff


class DashboardView(StaffView):
    def get(self, request):
        context = { 'dashboard_active': 'active' }
        return render(request, 'core/dashboard.html', context)


class TariffManagementView(StaffView):
    def get(self, request):
        context = {
            'tariff_active': 'active',
            'cities': City.objects.all(),
            'services': Service.objects.all()
        }
        return render(request, 'core/tariff-management.html', context)


class AgentManagementView(StaffView):
    def get(self, request):
        context = {
            'agent_active': 'active',
            'cities': City.objects.all(),
            'site_types': SiteType.objects.all()
            # 'site_types': SiteType.objects.filter(
            #     Q(name='Agen') | Q(name='Sub Agen')),
        }
        return render(request, 'core/agent-management.html', context)

class UserManagementView(StaffView):
    def get(self, request, site_pk):
        try:
            site = Site.objects.get(pk=site_pk)
        except Site.DoesNotExist:
            response = {
                'success': -1,
                'message': "Wrong identifier",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        context = {
            'site_pk': site_pk,
            'site_name': '[%s] %s' % (site.type, site.name)
        }
        return render(request, 'core/user-management.html', context)

class ReportView(StaffView):
    def get(self, request):
        context = { 'report_active': 'active', 'site': request.user.site }
        return render(request, 'agent/inventory.html', context)

    def post(self, request):
        report = SiteReport()
        response = report.print_blank(request)
        return response

class PickUpManagementView(StaffView):
    def get(self, request):
        agents = Site.objects.all()
        data = list()
        for agent in agents:
            items = ItemSite.objects.filter(site=agent.id)
            t = {
                    'dataagent' : agent,
                    'amount' : len(items),
            }
            data.append(t)
        
        context = {
            'pickup_active': 'active',
            'data': data,
        }
        return render(request, 'core/pickup-management.html', context)

class ManualScanManagementView(StaffView):
    def get(self, request):
        context = {
            'manualscan_active': 'active'
        }
        return render(request, 'core/manualscan-management.html', context)

class BaggingManagementView(StaffView):
    def get(self, request):
        context = {
            'bagging_active': 'active',
            'user_id': request.user.id
        }
        return render(request, 'core/bagging-management.html', context)

class ArrivalManagementView(StaffView):
    def get(self, request):
        context = {
            'arrival_active': 'active',
            'user_id': request.user.id,
            'status': ItemStatus.objects.get(id=3)
        }
        return render(request, 'core/arrival.html', context)

class ConsignmentNoteManagementView(StaffView):
    def get(self, request):
        context = {
            'consignment_active': 'active',
            'fill_active': 'active',
            'cities': City.objects.all().order_by('name'),
            'good_types': GoodType.objects.all(),
            'payment_types': PaymentType.objects.all(),
            'services': Service.objects.all(),
        }
        return render(request, 'core/consignment-note.html', context)

class ManifestingManagementView(StaffView):
    def get(self, request):
        context = {
            'manifesting_active': 'active',
            'transports': Transportation.objects.all().order_by('identifier'),
            'cities': City.objects.all().order_by('name'),
            'transport_type': TransportationType.objects.all().order_by('name')
        }
        return render(request, 'core/manifesting.html', context)

class AirportManagementView(StaffView):
    def get(self, request):
        context = {
            'airport_active': 'active',
            'transports': Transportation.objects.all().order_by('identifier'),
            'cities': City.objects.all().order_by('name'),
            'transport_type': TransportationType.objects.all().order_by('name')
        }
        return render(request, 'core/airport.html', context)

class ArrivalBagManagementView(StaffView):
    def get(self, request):
        context = {
            'arrival_bag_active': 'active'
        }
        return render(request, 'core/arrival-bag.html', context)

class ArrivalItemManagementView(StaffView):
    def get(self, request):
        context = {
            'arrival_item_active': 'active'
        }
        return render(request, 'core/arrival-item.html', context)

class DeliveryManagementView(StaffView):
    def get(self, request):
        context = {
            'delivery_active': 'active',
            'couriers': Courier.objects.filter(city_id=request.user.site.city.id) \
                                            .order_by('name'),
            'user_id': request.user.id
        }
        return render(request, 'core/delivery.html', context)

class DeliveryThirdPartyManagementView(StaffView):
    def get(self, request):
        context = {
            'delivery_third_active': 'active',
            'forwarders': Forwarder.objects.all().order_by('name')
        }
        return render(request, 'core/delivery-forwarder.html', context)

class DeliveryUpdateManagementView(StaffView):
    def get(self, request):
        context = {
            'delivery_update': 'active',
            'status': ItemStatus.objects.all().order_by('name')
        }
        return render(request, 'core/delivery-update.html', context)
