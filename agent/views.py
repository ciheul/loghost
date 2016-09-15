from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View

from core.models import City, GoodType, PaymentType, Service


class AgentView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return not self.request.user.is_staff


class DashboardView(AgentView):
    def get(self, request):
        context = { 'dashboard_active': 'active' }
        return render(request, 'agent/dashboard.html', context)


class FillView(AgentView):
    def get(self, request):
        context = {
            'fill_active': 'active',
            'cities': City.objects.all().order_by('name'),
            'good_types': GoodType.objects.all(),
            'payment_types': PaymentType.objects.all(),
            'services': Service.objects.all(),
        }
        return render(request, 'agent/fill.html', context)


class TrackView(AgentView):
    def get(self, request):
        context = { 'track_active': 'active' }
        return render(request, 'agent/track.html', context)


class TariffView(AgentView):
    def get(self, request):
        context = {
            'tariff_active': 'active',
            'cities': City.objects.all().order_by('name'),
        }
        return render(request, 'agent/tariff.html', context)


class ReportView(AgentView):
    def get(self, request):
        context = { 'report_active': 'active' }
        return render(request, 'agent/report.html', context)


class ProfileView(AgentView):
    def get(self, request):
        context = { 'profile_active': 'active' }
        return render(request, 'agent/profile.html', context)
