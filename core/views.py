from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View


class StaffView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff


class DashboardView(StaffView):
    def get(self, request):
        context = { 'dashboard_active': 'active' }
        return render(request, 'core/dashboard.html', context)
