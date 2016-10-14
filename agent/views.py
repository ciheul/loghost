from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View

from core.models import City, GoodType, PaymentType, Service
from report  import coree, agent
from report import agentnew


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

class FillMultipleView(AgentView):
    def get(self, request):
        context = {
            'fill_active': 'active',
            'cities': City.objects.all().order_by('name'),
            'good_types': GoodType.objects.all(),
            'payment_types': PaymentType.objects.all(),
            'services': Service.objects.all(),
        }
        return render(request, 'agent/fill-multiple.html', context)


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

    def get(self, request, item_id):
        report = agentnew.AgentReport()
        response = report.run(item_id)
        return response

    def post(self, request, item_id):
        report = agentnew.AgentReport()
        response = report.run(item_id)
        return response

class ReportMultipleView(AgentView):

    def get(self, request, item_id):
        report = agent.AgentReport()
        response = report.print_shipment_receipt_multiple_address(item_id)
        return response

    def post(self, request, item_id):
        report = agent.AgentReport()
        response = report.print_shipment_receipt_multiple_address(item_id)
        return response


class BlankReportView(AgentView):
    def post(self, request):
        report = coree.Report()
        response = report.run(request)
        return response

class NewReportView(AgentView):
    def post(self, request):
        report = agentnew.AgentReport()
        response = report.run(request)
        return response

class DeliveryReportView(AgentView):
    def post(self, request):
        report = agentnew.DeliveryReport()
        response = report.run(request)
        return response

class ManifestReportView(AgentView):
    def post(self, request):
        report = coree.ManifestReport()
        response = report.run(request)
        return response

class ShipmentView(AgentView):
    # def get(self, request):
    #     context = { 'shipment_active': 'active' }
    #     return render(request, 'agent/inventory.html', context)

    def post(self, request):
        report = agent.AgentReport()
        response = report.print_shipment_marking(request)
        return response


class ShipmentMarkingView(AgentView):
    # def get(self, request):
    #     context = { 'shipment_active': 'active' }
    #     return render(request, 'agent/inventory.html', context)

    def post(self, request, item_id):
        report = agent.AgentReport()
        response = report.print_shipment_marking(item_id)
        return response


class ShipmentReceiptView(AgentView):
    # def get(self, request):
    #     context = { 'shipment_active': 'active' }
    #     return render(request, 'agent/inventory.html', context)

    def post(self, request):
        report = agent.AgentReport()
        response = report.print_shipment_receipt_multiple_address(request)
        return response


class ProfileView(AgentView):
    def get(self, request):
        context = { 'profile_active': 'active' }
        return render(request, 'agent/profile.html', context)

class InventoryListView(AgentView):
    def get(self, request):
        context = { 'report_active': 'active', 'site': request.user.site }
        return render(request, 'agent/inventory.html', context)
