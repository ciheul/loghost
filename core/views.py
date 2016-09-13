from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View

from core.models import City, SiteType


class StaffView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff


class DashboardView(StaffView):
    def get(self, request):
        context = { 'dashboard_active': 'active' }
        return render(request, 'core/dashboard.html', context)


class AgentManagementView(StaffView):
    def get(self, request):
        context = {
            'management_active': 'active',
            'cities': City.objects.all(),
            'site_types': SiteType.objects.all(),
        }
        return render(request, 'core/agent-management.html', context)
