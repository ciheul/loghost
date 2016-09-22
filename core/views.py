from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View

from core.models import City, Service, Site, SiteType

from report.site import SiteReport

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
