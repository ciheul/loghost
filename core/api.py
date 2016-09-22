from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import DatabaseError, transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import View
from datetime import datetime
import simplejson as json

from account.models import CustomUser
from core.models import History, Item, ItemSite, ItemStatus, Site, Tariff, \
                        Shipment, ItemShipment, AWB, Bag, BagItem, \
                        ItemBagShipment, Incident, Delivery
from core.logics import generate_awb

import traceback, random, string

from report.site import SiteReport

class TariffCreateApi(View):
    def post(self, request):
        if not request.POST['origin'] \
                or not request.POST['destination'] \
                or not request.POST['service'] \
                or not request.POST['price'] \
                or not request.POST['duration']:
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # TODO error handling when site already exists
        # write to database
        try:
            s = Tariff(origin_id=int(request.POST['origin']),
                       destination_id=int(request.POST['destination']),
                       service_id=int(request.POST['service']),
                       price=int(request.POST['price']),
                       duration=request.POST['duration'])
            s.save()
        except DatabaseError:
            print traceback.format_exc()
            
            response = {
                'success': -1,
                'message': "Fail to create",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        response = { 'success': 0 }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class TariffReadApi(View):
    def get(self, request):
        tariffs = Tariff.objects.all()
        data = list()
        for tariff in tariffs:
            t = {
                'origin': tariff.origin.name,
                'origin_pk': tariff.origin.pk,
                'destination': tariff.destination.name,
                'destination_pk': tariff.destination.pk,
                'service': tariff.service.name,
                'service_pk': tariff.service.pk,
                'price': tariff.price,
                'duration': tariff.duration,
                'action': tariff.pk
            }
            data.append(t)

        response = { 'success': 0, 'data': data }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class TariffUpdateApi(View):
    def post(self, request):
        if not request.POST['pk'] \
                or not request.POST['origin'] \
                or not request.POST['destination'] \
                or not request.POST['service'] \
                or not request.POST['price'] \
                or not request.POST['duration']:
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # TODO error handling when site already exists
        # write to database
        try:
            t = Tariff.objects.get(pk=request.POST['pk'])
        except Site.DoesNotExist:
            response = {
                'success': -1,
                'message': "Fail to update",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        try:
            t.origin_id = int(request.POST['origin'])
            t.destination_id = int(request.POST['destination'])
            t.service_id = int(request.POST['service'])
            t.price = int(request.POST['price'])
            t.duration = request.POST['duration']
            t.save()
        except DatabaseError:
            print traceback.format_exc()
            
            response = {
                'success': -1,
                'message': "Fail to update",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        response = { 'success': 0 }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 



class TariffDeleteApi(View):
    def post(self, request):
        try:
            tariff = Tariff.objects.get(pk=int(self.request.POST['pk']))
            tariff.delete()
        except DatabaseError:
            print traceback.format_exc()
            response = {
                'success': -1,
                'message': "Fail to delete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        response = { 'success': 0 }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class TariffCheckApi(View):
    DIVIDER = 6000.0

    def get(self, request):
        if not request.GET['origin'] or not request.GET['destination']:
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # container to hold two kind of weights
        # normal weights and volumetric
        weights = list()

        # normal weights and calculated progressively
        if request.GET['weight']:
            weight = float(request.GET['weight'])
            if 0 < weight < 1:
                weight = 1
            weights.append(round(weight))

        if request.GET['length'] \
                and request.GET['width'] \
                and request.GET['height']:
            volume = float(request.GET['length']) \
                * float(request.GET['width']) \
                * float(request.GET['height'])

            weights.append(round(volume / self.DIVIDER))

        if len(weights) < 1: 
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # handling no route
        try:
            tariffs = Tariff.objects.filter(
                origin_id=request.GET['origin'],
                destination_id=request.GET['destination'])

            if len(tariffs) == 0:
                raise Tariff.DoesNotExist
        except Tariff.DoesNotExist:
            response = {
                'success': -1,
                'message': "No route",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        final_weight = max(weights)

        # TODO handling route
        data = list()
        for tariff in tariffs:
            d = {
                'origin': tariff.origin.name,
                'destination': tariff.destination.name,
                'service': tariff.service.name,
                'price': tariff.price * final_weight,
                'duration': tariff.duration,
            }
            data.append(d)

        response = {
            'success': 0,
            'weight': final_weight,
            'data': data
            # 'data': [
            #     { 'name': 'EXPRESS', 'type': 'Parcel', 'price': '18.000',
            #       'duration': '1-2'},
            #     { 'name': 'EXPRESS15', 'type': 'Parcel', 'price': '20.000',
            #       'duration': '1-2'},
            # ]
        }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class AgentCreateApi(View):
    def post(self, request):
        # form validation
        if not request.POST['name'] \
                or not request.POST['address'] \
                or not request.POST['city']:
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # TODO error handling when site already exists
        # write to database
        try:
            s = Site(name=request.POST['name'],
                     address=request.POST['address'],
                     city_id=int(request.POST['city']),
                     type_id=int(request.POST['type']))
            s.save()
        except DatabaseError:
            response = {
                'success': -1,
                'message': "Fail to create",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        response = { 'success': 0 }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class AgentReadApi(View):
    def get(self, request):
        # TODO use paging
        sites = Site.objects.filter(
            Q(type__name='Agen') | Q(type__name='Sub Agen'))

        data = list()
        for site in sites:
            d = {
                'pk': site.pk,
                'name': site.name,
                'address': site.address,
                'city': site.city.name,
                'city_pk': site.city.pk,
                'type': site.type.name,
                'type_pk': site.type.pk,
                'action': site.pk,
                'user_url': reverse('core-user',
                                    kwargs={ 'site_pk': site.pk})
            }
            data.append(d)

        response = { 'success': 0, 'data': data }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class AgentUpdateApi(View):
    def post(self, request):
        # form validation
        if not request.POST['pk'] \
                or not request.POST['name'] \
                or not request.POST['address'] \
                or not request.POST['city']:
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # TODO error handling when site already exists
        # write to database
        try:
            s = Site.objects.get(pk=request.POST['pk'])
        except Site.DoesNotExist:
            response = {
                'success': -1,
                'message': "Fail to update",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        try:
            s.name = request.POST['name']
            s.address = request.POST['address']
            s.city_id = int(request.POST['city'])
            s.type_id = int(request.POST['type'])
            s.save()
        except DatabaseError:
            response = {
                'success': -1,
                'message': "Fail to update",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        response = { 'success': 0 }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class AgentDeleteApi(View):
    def post(self, request):
        try:
            site = Site.objects.get(pk=int(self.request.POST['pk']))
            site.delete()
        except DatabaseError:
            response = {
                'success': -1,
                'message': "Fail to delete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        response = { 'success': 0 }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class UserCreateApi(View):
    def post(self, request):
        # form validation
        if not request.POST['name'] \
                or not request.POST['site_pk'] \
                or not request.POST['email'] \
                or not request.POST['password'] \
                or not request.POST['confirm']:
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # TODO error handling when site already exists
        # write to database
        try:
            s = CustomUser(fullname=request.POST['name'],
                           site_id=int(request.POST['site_pk']),
                           email=request.POST['email'],
                           password=make_password(request.POST['password']))
            s.save()
        except DatabaseError:
            response = {
                'success': -1,
                'message': "Fail to create",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        response = { 'success': 0 }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class UserReadApi(View):
    def get(self, request):
        users = CustomUser.objects.filter(site_id=request.GET['site_pk'])

        data = list()
        for user in users:
            u = {
                'name': user.fullname,
                'email': user.email,
                'action': user.pk,
            }
            data.append(u)

        response = { 'success': 0, 'data': data }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class UserUpdateApi(View):
    def post(self, request):
        # form validation
        # if not request.POST['name'] \
        #         or not request.POST['address'] \
        #         or not request.POST['city']:
        #     response = {
        #         'success': -1,
        #         'message': "Parameters are not complete",
        #     }
        #     return HttpResponse(json.dumps(response),
        #                         content_type='application/json') 
        #
        # # TODO error handling when site already exists
        # # write to database
        # try:
        #     s = Site.objects.get(pk=request.POST['pk'])
        # except Site.DoesNotExist:
        #     response = {
        #         'success': -1,
        #         'message': "Fail to update",
        #     }
        #     return HttpResponse(json.dumps(response),
        #                         content_type='application/json') 
        #
        # try:
        #     s.name = request.POST['name']
        #     s.address = request.POST['address']
        #     s.city_id = int(request.POST['city'])
        #     s.type_id = int(request.POST['type'])
        #     s.save()
        # except DatabaseError:
        #     response = {
        #         'success': -1,
        #         'message': "Fail to update",
        #     }
        #     return HttpResponse(json.dumps(response),
        #                         content_type='application/json') 

        response = { 'success': 0 }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class UserDeleteApi(View):
    def post(self, request):
        try:
            user = CustomUser.objects.get(pk=int(self.request.POST['user_pk']))
            user.delete()
        except DatabaseError:
            response = {
                'success': -1,
                'message': "Fail to delete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        response = { 'success': 0 }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class ItemCreateApi(View):
    def post(self, request):
        if not request.POST['sender_name'] \
                or not request.POST['sender_address'] \
                or not request.POST['sender_city'] \
                or not request.POST['receiver_name'] \
                or not request.POST['receiver_address'] \
                or not request.POST['receiver_city'] \
                or not request.POST['service'] \
                or not request.POST['good_type'] \
                or not request.POST['payment_type'] \
                or not request.POST['good_name'] \
                or not request.POST['price']:
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # normalize
        weight = request.POST['weight']
        length = request.POST['length']
        width = request.POST['width']
        height = request.POST['height']
        good_value = request.POST['good_value']
        sender_zip_code = request.POST['sender_zip_code']
        receiver_zip_code = request.POST['receiver_zip_code']

        if weight == '': weight = 0.0
        if length == '': length = 0.0
        if width == '': width = 0.0
        if height == '': height = 0.0
        if good_value == '': good_value = 0
        if sender_zip_code == '': sender_zip_code = None
        if receiver_zip_code == '': receiver_zip_code = None

        try:
            tariff = Tariff.objects.get(
                origin_id=int(request.POST['sender_city']),
                destination_id=int(request.POST['receiver_city']),
                service_id=int(request.POST['service']))
        except Tariff.DoesNotExist:
            response = {
                'success': -1,
                'message': "No route. Ensure tariff is available",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        awb = generate_awb()

        # TODO error handling when site already exists
        # write to database
        try:
            item = Item(user=request.user,
                        awb=awb,
                        sender_name=request.POST['sender_name'],
                        sender_address=request.POST['sender_address'],
                        sender_city_id=int(request.POST['sender_city']),
                        sender_zip_code=sender_zip_code,
                        sender_phone=request.POST['sender_phone'],
                        receiver_name=request.POST['receiver_name'],
                        receiver_address=request.POST['receiver_address'],
                        receiver_city_id=int(request.POST['receiver_city']),
                        receiver_zip_code=receiver_zip_code,
                        receiver_phone=request.POST['receiver_phone'],
                        payment_type_id=int(request.POST['payment_type']),
                        good_name=request.POST['good_name'],
                        good_value=int(good_value),
                        good_type_id=int(request.POST['good_type']),
                        quantity=1,
                        weight=round(float(weight)),
                        length=float(length),
                        width=float(width),
                        height=float(height),
                        price=int(request.POST['price']),
                        information=request.POST['note'],
                        instruction=request.POST['instruction'],
                        tariff=tariff)
            item.save()
        except DatabaseError as e:
            response = {
                'success': -1,
                'message': "Fail to create Item",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        status_to_be_collected = ItemStatus.objects.get(
            name__iexact='TO BE COLLECTED')
        try:
            #insert to item_site
            item_site = ItemSite(item=item,
                                 site=request.user.site,
                                 received_at=timezone.now(),
                                 received_by=request.user.fullname,
                                 item_status=status_to_be_collected)
            item_site.save()
        except DatabaseError as e:
            response = {
                'success': -1,
                'message': "Fail to create ItemSite",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        try:
            status = "SHIPMENT RECEIVED BY COUNTER [%s]" \
                % (request.user.site.city.name.upper()) 
            history = History(item=item, status=status)
            history.save()
        except DatabaseError:
            response = {
                'success': -1,
                'message': "Fail to create Item History",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        response = { 'success': 0, 'awb': awb }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class ItemTrackApi(View):
    def get(self, request):
        if not request.GET['awb']:
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        try:
            item = Item.objects.get(awb=request.GET['awb'])
            statuses = History.objects.filter(item=item).order_by('created_at')
        except History.DoesNotExist:
            response = {
                'success': -1,
                'message': "AWB does not exist in database",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        data = list()
        for status in statuses:
            d = {
                'time': status.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'status': status.status,
            }
            data.append(d)

        response = {
            'success': 0,
            'awb': item.awb,
            'service': item.tariff.service.name,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'sender_city_name': item.sender_city.name,
            'receiver_city_name': item.receiver_city.name,
            'good_type': item.good_type.name,
            'sender_name': item.sender_name,
            'sender_address': item.sender_address,
            'sender_zip_code': item.sender_zip_code,
            'data': data
        }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


class ItemSiteApi(View):
    def get(self, request, site_pk):
        data = list()
        item_sites = ItemSite.objects.filter(site_id=site_pk)
        for item_site in item_sites:
            d = {
                'received_at':
                    item_site.received_at.strftime('%Y-%m-%d %H:%M:%S'),
                'awb': item_site.item.awb,
                'rack_id': item_site.rack_id,
                'sender': item_site.item.sender_name,
                'origin': item_site.item.sender_city.name,
                'destination': item_site.item.receiver_city.name,
                'service': item_site.item.tariff.service.name,
                'status': item_site.item_status.name,
                'action': item_site.item.pk,
            }
            data.append(d)

        response = {
            'success': 0,
            'data': data,
        }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 


#user_id, shipment_id, awb_list, bag_id_list
class OutboundApi(View):
    
    def post(self, request):
        #if not request.POST['user_id'] \
        #    or not request.POST['shipment_id'] : \
        #    response = {
        #                'success': -1,
        #                'message': "Parameters are not complete",
        #    }

        #    return HttpResponse(json.dumps(response),
        #            content_type='application/json')

        # retrieve location
        user = None
        try:
            user = CustomUser.objects.get(pk=request.POST['user_id'])
        except:
            response = {
                    'success': -1,
                    'message': "Parameter is no valid"
                    }
            return HttpResponse(json.dumps(response),
                                content_type='application/json')

        outbound_status = ItemStatus.objects.get(code__iexact='OB')

        print 'test : ' + str(request.POST.getlist('bag_id_list'))
        try:
            
            bag_item_qs = BagItem.objects.filter(
                            bag_id__in=request.POST.getlist('bag_id_list'))
            awb_id_list = []
            for bag_item in list(bag_item_qs):
                awb_id_list.append(bag_item.awb_id)

            #insert to item_bag_shipment
            item_bag_list = []
            for bag_id in request.POST.getlist('bag_id_list'):
                item_bag_list.append(ItemBagShipment(
                                        shipment_id=request.POST['shipment_id'],
                                        bag_id=bag_id))
            ItemBagShipment.objects.bulk_create(item_bag_list)

            #insert to item shipment
            awb_qs = AWB.objects.filter(number__in=request.POST.getlist('awb_list'))
            item_shipment_list = []
            for item in list(awb_qs):
                awb_id_list.append(item.id)
                item_shipment_list.append(ItemShipment(
                                        shipment_id=request.POST['shipment_id'],
                                        awb_id=item.id))
            ItemShipment.objects.bulk_create(item_shipment_list)

            #update status awb
            AWB.objects.filter(pk__in=awb_id_list) \
                    .update(status_id=outbound_status.id)

            #update status item site
            ItemSite.objects.filter(awb_id__in=awb_id_list) \
                    .update(item_status_id=outbound_status.id)

            #insert to history
            history_list = []
            for awb_id in awb_id_list:
                history_list.append(History(
                                    awb_id=awb_id,
                                    status=outbound_status.name  \
                                            + ' [' + user.site.name + ']' ))
            History.objects.bulk_create(history_list)

        except:
            print traceback.format_exc()
            # return error response
            response = {
                'success': -1,
                'message': 'Database problem'
                }

            return HttpResponse(json.dumps(response),
                                content_type='application/json')

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                                        content_type='application/json')


#user_id, awb_list
class ItemOnProcess(View):
    def post(self, request):
        if not request.POST['user_id'] \
            or not request.POST['awb_list'] :
                response = {
                    'success': -1,
                    'message': "Parameters are not complete",
                }
                return HttpResponse(json.dumps(response),
                        content_type='application/json')

        user = None
        try:
            user = CustomUser.objects.get(pk=request.POST['user_id'])
        except:
            response = {
                    'success': -1,
                    'message': "Parameter is no valid"
                    }
            return HttpResponse(json.dumps(response),
                                content_type='application/json')

        try:
            on_process_status = ItemStatus.objects.get(code='OP')
            awb_id_list = []
            awb_qs = AWB.objects.filter(number__in=request.POST.getlist('awb_list'))

            for awb in list(awb_qs):
                awb_id_list.append(awb.id)

            # update awb
            AWB.objects.filter(pk__in=awb_id_list) \
                    .update(status_id=on_process_status.id)
            # update itemsite
            ItemSite.objects.filter(Q(site_id=user.site.id) and 
                            Q(awb_id__in=awb_id_list)) \
                            .update(item_status_id=on_process_status.id)
            # insert history
            history_list = []
            for awb_id in awb_id_list:
                history_list.append(History(awb_id=awb_id, 
                        status=on_process_status.name))
            History.objects.bulk_create(history_list)
        except:
            print traceback.format_exc()
            
            # return error response
            response = {
                'success': -1,
                'message': 'Database problem'
                }
            return HttpResponse(json.dumps(response),
                                content_type='application/json')

        
        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')


#user_id, awb_list
class ItemProcessed(View):
    def post(self, request):
        if not request.POST['user_id'] \
            or not request.POST['awb_list'] :
                response = {
                    'success': -1,
                    'message': "Parameters are not complete",
                }
                return HttpResponse(json.dumps(response),
                        content_type='application/json')

        user = None
        try:
            user = CustomUser.objects.get(pk=request.POST['user_id'])
        except:
            response = {
                    'success': -1,
                    'message': "Parameter is no valid"
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')


        try:
            processed_status = ItemStatus.objects.get(code='PR')
            awb_id_list = []
            awb_qs = AWB.objects.filter(number__in=request.POST.getlist('awb_list'))

            for awb in list(awb_qs):
                awb_id_list.append(awb.id)

            # update awb
            AWB.objects.filter(pk__in=awb_id_list) \
                    .update(status_id=processed_status.id)
            # update itemsite
            ItemSite.objects.filter(Q(site_id=user.site.id) and 
                            Q(awb_id__in=awb_id_list)) \
                            .update(status_id=processed_status.id)
            # insert history
            history_list = []
            for awb_id in awb_id_list:
                history_list.append(History(awb_id=awb_id, 
                        status=processed_status.name))
            History.objects.bulk_create(history_list)
        except:
            print traceback.format_exc()
            
            # return error response
            response = {
                'success': -1,
                'message': 'Database problem'
                }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        
        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')


#user_id, bag_number, awb_list
class BaggingApi(View):
    def post(self, request):
        if not request.POST['user_id'] \
                or not request.POST['bag_number'] \
                or not request.POST.getlist('awb_list'):
                    response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
                    return HttpResponse(json.dumps(response),
                                        content_type='application/json')
                    
        
        # create relation between bag and item/awb
        bag, created = Bag.objects.get_or_create(number=request.POST['bag_number'])
        processed_status = ItemStatus.objects.get(code='PR')
        
        # clear previous assignment
        if created is False:
            BagItem.objects.filter(bag_id=bag.id).delete()

        try:
            awb_qs = AWB.objects.filter( \
                    number__in=request.POST.getlist('awb_list'))

            awb_id_list= []
            for awb in list(awb_qs):
                awb_id_list.append(awb.id)

            #update awb status
            AWB.objects.filter(pk__in=awb_id_list) \
                    .update(status_id=processed_status.id)

            #update item site status
            ItemSite.objects.filter(awb_id__in=awb_id_list) \
                    .update(item_status_id=processed_status.id)

            #insert bag item and hisotry
            bag_item_list = []
            history_list = []
            for awb_id in awb_id_list:
                bag_item_list.append(BagItem(
                                        bag_id= bag.id,
                                        awb_id=awb_id))
                history_list.append(History(
                                awb_id=awb_id,
                                status= processed_status.name))
            BagItem.objects.bulk_create(bag_item_list)
            History.objects.bulk_create(history_list)

        except:
            print traceback.format_exc()
            
            # return error response
            response = {
                'success': -1,
                'message': 'Database problem'
                }
            return HttpResponse(json.dumps(response),
                content_type='application/json')

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')


            
#user_id, awb_list
class InboundApi(View):
    
    def post(self, request):
        if not request.POST['user_id'] \
                or not request.POST.getlist('awb_list') : 
                    response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
                    return HttpResponse(json.dumps(response),
                                        content_type='application/json')
        # retrieve location
        user = None
        try:
            user = CustomUser.objects.get(pk=request.POST['user_id'])
        except:
            response = {
                    'success': -1,
                    'message': "User is not valid"
                    }
            return HttpResponse(json.dumps(response),
                                content_type='application/json')

        #location = Site.objects.get(pk=user.site.id)

        arrived_status = ItemStatus.objects.get(code='AF')

        #TODO distinct awb and bag_id
        # check whether parameter is indeed awb or bag_id
        bag_id_list = []
        awb_list = []
        
        for item in request.POST.getlist('awb_list'):
            if item.startswith('BAG'):
                bag_id_list.append(item)
            else:
                awb_list.append(item)

        try:
            bag_item_qs = BagItem.objects.filter(bag_id__in=bag_id_list)
            
            awb_id_list = []
            #append awb_id to list from BagItem
            for bag_item in list(bag_item_qs):
                awb_id_list.append(bag_item.awb_id)

            #append awb_id to list from AWB
            awb_qs = AWB.objects.filter(number__in=awb_list)
            for awb in list(awb_qs):
                awb_id_list.append(awb.id)

            print str(awb_id_list)
            #update status AWB
            AWB.objects.filter(pk__in=awb_id_list) \
                    .update(status_id=arrived_status.id)
            
            # insert item site and history
            item_site_list = []
            history_list = []
            for awb_id in awb_id_list:
                item_site_list.append(ItemSite(
                                        awb_id=awb_id,
                                        site_id=user.site.id,
                                        received_at=timezone.now(),
                                        received_by=user.fullname,
                                        item_status_id=arrived_status.id))
                history_list.append(History(
                                        awb_id=awb_id,
                                        status=arrived_status.name \
                                                + '[ ' + user.site.name + ']'))
            ItemSite.objects.bulk_create(item_site_list)
            History.objects.bulk_create(history_list)
        except:
            print traceback.format_exc()
            response = {
                    'success': -1,
                    'message': "Database problem"
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')

class ItemInsertApi(View):

    def post(self, request):

        # retrieve location
        user = CustomUser.objects.get(pk=request.POST['user_id'])
        location = Site.objects.get(pk=user.site_id)
        # TODO still hardcode
        detail_entry_status = ItemStatus.objects.get(code__exact='SD')
        
        awb = self.get_awb_number(detail_entry_status.id)
        
        try:
            if awb is None:
                response = {
                    'success': -1,
                    'message': 'Awb generation failed'
                    }
                return HttpResponse(json.dumps(response),
                                     content_type='application/json')

            #create item
            item = Item(
                    user_id=user.id,
                    awb_id=awb.id,
                    sender_name=request.POST['sender_name'],
                    sender_address=request.POST['sender_address'],
                    sender_zip_code=request.POST['sender_zip_code'],
                    receiver_name=request.POST['receiver_name'],
                    receiver_address=request.POST['receiver_address'],
                    receiver_zip_code=request.POST['receiver_zip_code'],
                    quantity=request.POST['quantity'],
                    good_type_id=request.POST['good_type_id'],
                    payment_type_id=request.POST['payment_type_id'],
                    tariff_id=request.POST['tariff_id'],
                    good_name=request.POST['good_name'])

            item.sender_city_id=int(request.POST['sender_city_id'])
            item.receiver_city_id=int(request.POST['receiver_city_id'])
            item.status_id=detail_entry_status.id
            item.save()

            #insert to item_site
            item_site = ItemSite(
                            awb_id=awb.id,
                            site_id=location.id,
                            received_at=timezone.now(),
                            received_by=user.fullname)
            item_site.item_status_id=detail_entry_status.id
            item_site.save()


            #insert to History
            history = History(
                        awb_id=awb.id,
                        status=detail_entry_status.name \
                                + ' [' + location.name +']')
            history.save()

        except:
            print traceback.format_exc()
            self.release_awb(awb)
            response = {
                'success': -1,
                'message': 'Database Problem'
                }
            return HttpResponse(json.dumps(response),
                            content_type='application/json')
            

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                    content_type='application/json')


    # get available awb that has no status in it
    def get_awb_number(self, status_id):
        awb_number = None
        try:
            awb_number = AWB.objects.filter(status__isnull=True).order_by('pk')[0]
            # update status of awb to SD
            awb_number.status_id = status_id
            awb_number.save()
        except:
            print traceback.format_exc()
            return None
        return awb_number

    def release_awb(self, awb):
        awb.status = None
        awb.save()


#user_id, transportation_id, cost, destination_site_id
class RunsheetCreateApi(View):

    def post(self, request):
        if not request.POST['user_id'] \
                or not request.POST['destination_site_id'] \
                or not request.POST['transportation_id'] : 
            response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        user = CustomUser.objects.get(pk=request.POST['user_id'])

        # TODO need mechanism to check whether runsheet has been generated 
        #       to avoid staff to generate DOUBLE runsheet

       
        try:
            # create runsheet
            runsheet = Shipment(
                cost=request.POST['cost'],
                transportation_id=request.POST['transportation_id'])
            runsheet.origin_site_id = user.site.id
            runsheet.destination_site_id = request.POST['destination_site_id']
            runsheet.save()
        except:
            print traceback.format_exc()
            response = {
                'success': -1,
                'message': 'Database Problem'
                }
            return HttpResponse(json.dumps(response),
                    content_type='application/json')

        
           
        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')


#user_id, shipment_id, smu
class RunsheetUpdateApi(View):
    def post(self, request):
        if not request.POST['user_id'] \
                or not request.POST['smu'] \
                or not request.POST['shipment_id'] : 
            response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        user = CustomUser.objects.get(pk=request.POST['user_id'])
        
        try:
            # update smu
            Shipment.objects.filter(pk=request.POST['shipment_id']) \
                    .update(smu=request.POST['smu'])
        except:
            print traceback.format_exc()
            response = {
                'success': -1,
                'message': 'Database Problem'
                }
            return HttpResponse(json.dumps(response),
                    content_type='application/json')

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')


#user_id, status_code, awb, information
class ItemIncidentApi(View):

     def post(self, request):
        if not request.POST['user_id'] \
                or not request.POST['status_code'] \
                or not request.POST['awb'] \
                or not request.POST['information'] : 
            response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        user = None
        try:
            user = CustomUser.objects.get(pk=request.POST['user_id'])
        except:
            response = {
                    'success': -1,
                    'message': "Parameter is no valid"
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        try:
            status = ItemStatus.objects.get(code=request.POST['status_code'])
            awb = AWB.objects.get(number=request.POST['awb'])
            awb.status_id = status.id
            awb.save()
            
            Incident(awb_id=awb.id, 
                    site_id=user.site.id,
                    status_id=status.id,
                    information=request.POST['information']).save()

            History(awb_id=awb.id,
                    status=status.name).save()
                    
        except:
            print traceback.format_exc()
            response = {
                    'success': -1,
                    'message': "Database Problem"
                    }
            return HttpResponse(json.dumps(response),
                                content_type='application/json')

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')


#user_id, awb_list, courier_id
class ItemDeliveryCreateApi(View):
    def post(self, request):
        if not request.POST['user_id'] \
                or not request.POST.getlist('awb_list'):
            response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        if not request.POST['courier_id'] \
            and not request.POST['forwarder_id']:
            response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')
        
        user = None
        try:
            user = CustomUser.objects.get(pk=request.POST['user_id'])
        except:
            response = {
                    'success': -1,
                    'message': "Parameter is no valid"
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        is_courier = True
        if not request.POST['courier_id']:
            is_courier = False

        awb_qs = AWB.objects.filter( \
                    number__in=request.POST.getlist('awb_list'))

        awb_id_list = []
        for awb in list(awb_qs):
            awb_id_list.append(awb.id)

        try:
            status = None
            
            history_list = []
            delivery_list = []
            if is_courier:
                status = ItemStatus.objects.get(code='WC')
                AWB.objects.filter(pk__in=awb_id_list) \
                    .update(status_id=status.id)

                for awb_id in awb_id_list:
                    delivery_list.append(Delivery(
                                        awb_id=awb_id,
                                        courier_id=request.POST['courier_id'],
                                        status_id=status.id,
                                        site_id=user.site.id))
                    history_list.append(History(
                                        awb_id=awb_id,
                                        status = status.name))

                                
            else:
                status = ItemStatus.objects.get(code='FW')
                AWB.objects.filter(pk__in=awb_id_list) \
                    .update(status_id=status.id)

                for awb_id in awb_id_list:
                    delivery_list.append(Delivery(
                                        awb_id=awb_id,
                                        forwarder_id=request.POST['forwarder_id'],
                                        status_id=status.id,
                                        site_id=user.site.id))
                    history_list.append(History(
                                        awb_id=awb_id,
                                        status = status.name))

            ItemStatus.objects.filter(
                                site_id=user.site.id,
                                awb_id__in=awb_id_list).update(
                                status=status.id)
            Delivery.objects.bulk_create(delivery_list)
            History.objects.bulk_create(history_list)


        except:
            print traceback.format_exc()
            response = {
                    'success': -1,
                    'message': "Database problem"
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')


# user_id, courier_id | forwarder_id, awb, status_code,
# receiver_name, receive_date
class ItemDeliveryUpdateApi(View):
    def post(self, request):
        if not request.POST['user_id'] \
                or not request.POST.getlist('awb'):
            response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        if not request.POST['courier_id'] \
            and not request.POST['forwarder_id']:
            response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')
        
        user = None
        delivery_status = None
        try:
            user = CustomUser.objects.get(pk=request.POST['user_id'])
            delivery_status = ItemStatus.objects.get( 
                                        code=request.POST['status_code'])
        except:
            response = {
                    'success': -1,
                    'message': "Parameter is no valid"
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        is_courier = True
        if not request.POST['courier_id']:
            is_courier = False

        

        try:
            awb = AWB.objects.get(number=request.POST['awb'])
            if is_courier:
                status = ItemStatus.objects.get(code='WC')
                Delivery.objects.filter(site_id=user.site.id, 
                                        awb_id=awb.id,
                                        status_id=status.id,
                                        courier_id=request.POST['courier_id']) \
                                .update(status_id=delivery_status.id,
                                        receiver_name=request.POST['receiver_name'],
                                        receive_date=self.convert_to_datetime(
                                            request.POST['receive_date']))
                awb.status_id=delivery_status.id
                awb.save()
                ItemSite.objects.filter(site_id=user.site.id,
                                            item_status_id=status.id,
                                            awb_id=awb.id) \
                                .update(item_status_id=delivery_status.id)
                
                
            else:
                status = ItemStatus.objects.get(code='FW')
                Delivery.objects.filter(site_id=user.site.id, 
                                        awb_id=awb.id,
                                        status_id=status.id,
                                        courier_id=request.POST['forwarder_id'])\
                                .update(status_id=delivery_status.id,
                                        receiver_name=request.POST['receiver_name'],
                                        receive_date=self.convert_to_datetime(
                                            request.POST['receive_date']))
                awb.status_id=delivery_status.id
                awb.save()
                ItemSite.objects.filter(site_id=user.site.id,
                                            item_status_id=status.id,
                                            awb_id=awb.id) \
                                    .update(item_status_id=delivery_status.id)

            History(awb_id=awb.id, 
                        status=delivery_status.name \
                                + ' [' + request.POST['receiver_name'] + ' at ' \
                                + request.POST['receive_date'] + ']').save()
        except:
            print traceback.format_exc()
            response = {
                    'success': -1,
                    'message': "Database problem"
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')
       


    # format date in string: Sep 1 2016  1:33PM
    def convert_to_datetime(self, date_in_string):
        return datetime.strptime(date_in_string, '%b %d %Y %I:%M%p')
        
# user_id, courier_id | forwarder_id, awb, status_code
class ItemDeliveryUpdateFailApi(View):
    def post(self, request):
        if not request.POST['user_id'] \
                or not request.POST.getlist('awb'):
            response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        if not request.POST['courier_id'] \
            and not request.POST['forwarder_id']:
            response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')
        
        user = None
        delivery_status = None
        try:
            user = CustomUser.objects.get(pk=request.POST['user_id'])
            delivery_status = ItemStatus.objects.get( 
                                        code=request.POST['status_code'])
        except:
            response = {
                    'success': -1,
                    'message': "Parameter is no valid"
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        is_courier = True
        if not request.POST['courier_id']:
            is_courier = False

        

        try:
            awb = AWB.objects.get(number=request.POST['awb'])
            if is_courier:
                status = ItemStatus.objects.get(code='WC')
                Delivery.objects.filter(site_id=user.site.id, 
                                        awb_id=awb.id,
                                        status_id=status.id,
                                        courier_id=request.POST['courier_id']) \
                                .update(status_id=delivery_status.id)
                awb.status_id=delivery_status.id
                awb.save()
                ItemSite.objects.filter(site_id=user.site.id,
                                            item_status_id=status.id,
                                            awb_id=awb.id) \
                                .update(item_status_id=delivery_status.id)
                
                
            else:
                status = ItemStatus.objects.get(code='FW')
                Delivery.objects.filter(site_id=user.site.id, 
                                        awb_id=awb.id,
                                        status_id=status.id,
                                        courier_id=request.POST['forwarder_id'])\
                                .update(status_id=delivery_status.id)
                awb.status_id=delivery_status.id
                awb.save()
                ItemSite.objects.filter(site_id=user.site.id,
                                            item_status_id=status.id,
                                            awb_id=awb.id) \
                                    .update(item_status_id=delivery_status.id)

            History(awb_id=awb.id, 
                        status=delivery_status.name).save()

        except:
            print traceback.format_exc()
            response = {
                    'success': -1,
                    'message': "Database problem"
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')

class ReportSiteApi(View):
    def post(self, request):
        report = SiteReport()
        response = report.print_blank(request)
        return HttpResponse(json.dumps(response), content_type='application/pdf')

    # format date in string: Sep 1 2016  1:33PM
    def convert_to_datetime(self, date_in_string):
        return datetime.strptime(date_in_string, '%b %d %Y %I:%M%p')

