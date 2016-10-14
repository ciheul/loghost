from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import DatabaseError, transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import View
from datetime import datetime

from bulk_update.helper import bulk_update
import simplejson as json

from account.models import CustomUser
from core.models import History, Item, ItemSite, ItemStatus, Site, Tariff, \
                        Shipment, ItemShipment, AWB, Bag, BagItem, \
                        ItemBagShipment, Incident, Transportation, Delivery, Courier
from core.logics import generate_awb

import traceback, random, string


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
        # form validation
        # TODO error handling
        print('sender name: ' + str(request.POST.getlist('sender_address')))
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

        # check route
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

        sd_item_status = ItemStatus.objects.get(code__exact='SD')

        # TODO create AWB Generator
        awb = self.get_awb_number(sd_item_status.id)
        if awb is None:
            response = {
                'success': -1,
                'message': 'Awb generation failed'
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

        # insert to item_site.
        # if agent inserts the item, the physical item is still in agent office
        # if branch office inserts the item, indeed, the physical item has
        # been received in the sorting facility/branch office
        try:
            item_site = ItemSite(awb=awb,
                                 site=request.user.site,
                                 received_at=timezone.now(),
                                 received_by=request.user.fullname,
                                 item_status=sd_item_status)
            item_site.save()
        except DatabaseError as e:
            response = {
                'success': -1,
                'message': "Fail to create ItemSite",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        try:
            # status = "SHIPMENT RECEIVED BY COUNTER [%s]" \
            #     % (request.user.site.city.name.upper()) 
            history = History(awb=awb,
                              status=sd_item_status.name \
                                     + ' [' + request.user.site.name + ']')
            history.save()
        except DatabaseError:
            response = {
                'success': -1,
                'message': "Fail to create Item History",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        response = { 'success': 0, 'awb': awb.number, 'id': item.id}
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 

    # TODO maybe this method should be refactored out
    # so that other methods can call
    # get available awb that has no status in it
    def get_awb_number(self, status_id):
        awb_number = None
        try:
            # TODO perhaps this line sucks memory a lot
            awb_number = AWB.objects.filter(status__isnull=True) \
                .order_by('pk')[0]
            # update status of awb to SD
            awb_number.status_id = status_id
            awb_number.save()
        except:
            # print traceback.format_exc()
            return None
        return awb_number

    def release_awb(self, awb):
        awb.status = None
        awb.save()

class AgentItemCreateApi(View):
    def post(self, request):
        # form validation
        # TODO error handling
        print('sender name: ' + str(request.POST.getlist('sender_address')))
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

        # check route
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

        sd_item_status = ItemStatus.objects.get(code__exact='SD')

        # TODO create AWB Generator
        awb = self.get_awb_number(sd_item_status.id)
        if awb is None:
            response = {
                'success': -1,
                'message': 'Awb generation failed'
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

        # insert to item_site.
        # if agent inserts the item, the physical item is still in agent office
        # if branch office inserts the item, indeed, the physical item has
        # been received in the sorting facility/branch office
        try:
            item_site = ItemSite(awb=awb,
                                 site=request.user.site,
                                 received_at=timezone.now(),
                                 received_by=request.user.fullname,
                                 item_status=sd_item_status)
            item_site.save()
        except DatabaseError as e:
            response = {
                'success': -1,
                'message': "Fail to create ItemSite",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        try:
            # status = "SHIPMENT RECEIVED BY COUNTER [%s]" \
            #     % (request.user.site.city.name.upper()) 
            history = History(awb=awb,
                              status=sd_item_status.name \
                                     + ' [' + request.user.site.name + ']')
            history.save()
        except DatabaseError:
            response = {
                'success': -1,
                'message': "Fail to create Item History",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        response = { 'success': 0, 'awb': awb.number, 'id': item.id}
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 

    # TODO maybe this method should be refactored out
    # so that other methods can call
    # get available awb that has no status in it
    def get_awb_number(self, status_id):
        awb_number = None
        try:
            # TODO perhaps this line sucks memory a lot
            awb_number = AWB.objects.filter(status__isnull=True) \
                .order_by('pk')[0]
            # update status of awb to SD
            awb_number.status_id = status_id
            awb_number.save()
        except:
            # print traceback.format_exc()
            return None
        return awb_number

    def release_awb(self, awb):
        awb.status = None
        awb.save()

class ItemCreateMultiApi(View):
    def post(self, request):
        # form validation
        # TODO error handling
        if not request.POST.getlist('sender_name') \
                or not request.POST.getlist('sender_address') \
                or not request.POST.getlist('sender_city') \
                or not request.POST.getlist('receiver_name') \
                or not request.POST.getlist('receiver_address') \
                or not request.POST.getlist('receiver_city') \
                or not request.POST.getlist('service') \
                or not request.POST.getlist('good_type') \
                or not request.POST.getlist('payment_type') \
                or not request.POST.getlist('good_name') \
                or not request.POST.getlist('price'):
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # check route
        tariff_list = []
        sender_city_list = []
        destination_city_list = []
        service_list = []
        sender_cities = request.POST.getlist('sender_city')
        for sender_city in sender_cities:
            sender_city_list.append(sender_city)

        destination_cities = request.POST.getlist('receiver_city')
        for destination_city in destination_cities:
            destination_city_list.append(destination_city)

        services = request.POST.getlist('service')
        for service in services:
            service_list.append(service)

        for i in range(len(sender_city_list)):
            try:
                tariff = Tariff.objects.get(
                    origin_id=int(sender_city_list[i]),
                    destination_id=int(destination_city_list[i]),
                    service_id=int(service_list[i]))
            
                tariff_list.append(str(tariff.id))
            except Tariff.DoesNotExist:
                response = {
                    'success': -1,
                    'message': "No route. Ensure tariff is available",
                }
                return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        print(tariff_list[0])
        sd_item_status = ItemStatus.objects.get(code__exact='SD')

        # TODO create AWB Generator
        awb_list = []
        
        for i in range(len(destination_city_list)):
            awb = self.get_awb_number(sd_item_status.id)
            if awb is None:
                response = {
                    'success': -1,
                    'message': 'Awb generation failed'
                }   
                return HttpResponse(json.dumps(response),
                                content_type='application/json')
            awb_list.append(awb)
        # normalize
        weights = request.POST.getlist('weight')
        lengths = request.POST.getlist('length')
        widths = request.POST.getlist('width')
        heights = request.POST.getlist('height')
        good_values = request.POST.getlist('good_value')
        sender_zip_codes = request.POST.getlist('sender_zip_code')
        receiver_zip_codes = request.POST.getlist('receiver_zip_code')

        weight_list = []
        length_list = []
        width_list = []
        height_list = []
        good_value_list = []
        sender_zip_code_list = []
        receiver_zip_code_list = []

        for weight in weights:
            if weight == '':
                weight = 0.0
            weight_list.append(weight)

        for length in lengths:
            if length == '':
                length = 0.0
            length_list.append(length)

        for width in widths:
            if width == '':
                width = 0.0
            width_list.append(width)

        for height in heights:
            if height == '':
                height = 0.0
            height_list.append(height)

        for good_value in good_values:
            if good_value == '':
                good_value = 0
            good_value_list.append(good_value)

        for sender_zip_code in sender_zip_codes:
            if sender_zip_code == '':
                sender_zip_code = None
            sender_zip_code_list.append(sender_zip_code)

        for receiver_zip_code in receiver_zip_codes:
            if receiver_zip_code == '':
                receiver_zip_code = None
            receiver_zip_code_list.append(receiver_zip_code)

        # TODO error handling when site already exists
        # write to database
        sender_name_list = []
        sender_address_list = []
        sender_city_list = []
        sender_phone_list = []

        receiver_name_list = []
        receiver_address_list = []
        receiver_city_list = []
        receiver_phone_list = []
        
        payment_type_list = []
        good_name_list = []
        good_type_list = []
        price_list = []
        information_list = []
        instruction_list = []
        tariff_id_list = []
        
        sender_names = request.POST.getlist('sender_name')
        for sender_name in sender_names:
            sender_name_list.append(sender_name)

        sender_addresses = request.POST.getlist('sender_address')
        for sender_address in sender_addresses:
            sender_address_list.append(sender_address)

        sender_cities = request.POST.getlist('sender_city')
        for sender_city in sender_cities:
            sender_city_list.append(sender_city)

        sender_phones = request.POST.getlist('sender_phone')
        for sender_phone in sender_phones:
            sender_phone_list.append(sender_phone)

        receiver_names = request.POST.getlist('receiver_name')
        for receiver_name in receiver_names:
            receiver_name_list.append(receiver_name)

        receiver_addresses = request.POST.getlist('receiver_address')
        for receiver_address in receiver_addresses:
            receiver_address_list.append(receiver_address)

        receiver_cities = request.POST.getlist('receiver_city')
        for receiver_city in receiver_cities:
            receiver_city_list.append(receiver_city)

        receiver_phones = request.POST.getlist('receiver_phone')
        for receiver_phone in receiver_phones:
            receiver_phone_list.append(receiver_phone)

        payment_types = request.POST.getlist('payment_type')
        for payment_type in payment_types:
            payment_type_list.append(payment_type)

        good_names = request.POST.getlist('good_name')
        for good_name in good_names:
            good_name_list.append(good_name)

        good_types = request.POST.getlist('good_type')
        for good_type in good_types:
            good_type_list.append(good_type)

        prices = request.POST.getlist('price')
        for price in prices:
            price_list.append(price)

        informations = request.POST.getlist('information')
        for information in informations:
            information_list.append(information)

        instructions = request.POST.getlist('instruction')
        for instruction in instructions:
            instruction_list.append(instruction)

        #tariffs = tariff_list
        #for tariff in tariff_list:
        #    print('tariff id : ' + tariff.id)
        #    tariff_id_list.append(tariff)
        
        try:
            item_list = []
            for i in range(len(sender_name_list)) :
                current_tariff_id = tariff_list[i]
                item_list.append(Item(user=request.user,
                        awb=awb_list[i],
                        sender_name=sender_name_list[i],
                        sender_address=sender_address_list[i],
                        sender_city_id=int(sender_city_list[i]),
                        sender_zip_code=sender_zip_code_list[i],
                        sender_phone=sender_phone_list[i],
                        receiver_name=receiver_name_list[i],
                        receiver_address=receiver_address_list[i],
                        receiver_city_id=int(receiver_city_list[i]),
                        receiver_zip_code=receiver_zip_code_list[i],
                        receiver_phone=receiver_phone_list[i],
                        payment_type_id=int(payment_type_list[i]),
                        good_name=good_name_list[i],
                        good_value=int(good_value_list[i]),
                        good_type_id=int(good_type_list[i]),
                        quantity=1,
                        weight=round(float(weight_list[i])),
                        length=float(length_list[i]),
                        width=float(width_list[i]),
                        height=float(height_list[i]),
                        price=int(price_list[i]),
                        information=information_list[i],
                        instruction=instruction_list[i],
                        tariff_id=current_tariff_id)) 
            Item.objects.bulk_create(item_list)
        except DatabaseError as e:
            response = {
                'success': -1,
                'message': "Fail to create Item",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # insert to item_site.
        # if agent inserts the item, the physical item is still in agent office
        # if branch office inserts the item, indeed, the physical item has
        # been received in the sorting facility/branch office
        try:
            item_site_list = []
            for i in range(len(receiver_name_list)):
                item_site_list.append(ItemSite(awb=awb_list[i],
                                 site=request.user.site,
                                 received_at=timezone.now(),
                                 received_by=request.user.fullname,
                                 item_status=sd_item_status))

            ItemSite.objects.bulk_create(item_site_list)
        except DatabaseError as e:
            response = {
                'success': -1,
                'message': "Fail to create ItemSite",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        try:
            # status = "SHIPMENT RECEIVED BY COUNTER [%s]" \
            #     % (request.user.site.city.name.upper()) 
            history_list = []
            for i in range(len(sender_name_list)):
                history_list.append(History(awb=awb_list[i],
                              status=sd_item_status.name \
                                     + ' [' + request.user.site.name + ']'))

            History.objects.bulk_create(history_list)
        except DatabaseError:
            response = {
                'success': -1,
                'message': "Fail to create Item History",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        item_id_list = []
        for item in item_list:
            item_id_list.append(item.id)

        awb_number_list = []
        for awb in awb_list:
            awb_number_list.append(awb.number)
        
        response = { 'success': 0, 'awb': awb_number_list, 'id': item_id_list}
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 

    # TODO maybe this method should be refactored out
    # so that other methods can call
    # get available awb that has no status in it
    def get_awb_number(self, status_id):
        awb_number = None
        try:
            # TODO perhaps this line sucks memory a lot
            awb_number = AWB.objects.filter(status__isnull=True) \
                .order_by('pk')[0]
            # update status of awb to SD
            awb_number.status_id = status_id
            awb_number.save()
        except:
            # print traceback.format_exc()
            return None
        return awb_number

    def release_awb(self, awb):
        awb.status = None
        awb.save()



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
            item = Item.objects.get(awb__number=request.GET['awb'])
            # item = Item.objects.get(awb_id=request.GET['awb'])
            statuses = History.objects.filter(awb__number=request.GET['awb']) \
                .order_by('created_at')
            # statuses = History.objects.filter(item=item).order_by('created_at')
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
            'awb': request.GET['awb'],
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
            # NOTE this line satisfies when AWB is not reusable
            item = Item.objects.filter(awb=item_site.awb).order_by('-id')[0]
            d = {
                'received_at':
                    item_site.received_at.strftime('%Y-%m-%d %H:%M:%S'),
                'awb': item_site.awb.number,
                'sender': item.sender_name,
                'origin': item.sender_city.name,
                'destination': item.receiver_city.name,
                'service': item.tariff.service.name,
                'status': item.awb.status.name,
                'action': item.pk,
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
        print 'shipment_id: '+ request.POST['shipment_id']
        
        runsheet = Shipment(
                transportation_id=request.POST['shipment_id'])
        runsheet.origin_site_id = user.site.id
        runsheet.destination_site_id = request.POST['destination_id']
        runsheet.sent_by = user.fullname
        runsheet.sent_at = datetime.now()
        runsheet.origin = user.site.address
        runsheet.save()
        
        bag_number_list = []
        bag_id_list = []
        
        for item in request.POST.getlist('bag_id_list'):
            bag_number_list.append(item)
        
        try:
            bag_id_qs = Bag.objects.filter(number__in=bag_number_list)
            for bag in list(bag_id_qs):
                bag_id_list.append(bag.id)

            bag_item_qs = BagItem.objects.filter(
                            bag_id__in=bag_id_list)
            awb_id_list = []
            for bag_item in list(bag_item_qs):
                awb_id_list.append(bag_item.awb_id)

            #insert to item_bag_shipment
            item_bag_list = []
            for bag_id in bag_id_list:
                print request.POST['shipment_id']
                item_bag_list.append(ItemBagShipment(
                                        shipment_id=request.POST['shipment_id'],
                                        bag_id=bag_id))
            ItemBagShipment.objects.bulk_create(item_bag_list)

            #insert to item shipment
            print str(request.POST.getlist('awb_list'))
            awb_qs = AWB.objects.filter(number__in=request.POST.getlist('awb_list'))
            print ' stl q : ' + str(list(awb_qs))
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
            print 'list' + str(history_list)

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

class BaggingListApi(View):
    def get(self, request):
        # TODO use paging
        bags = Bag.objects.all()

        data = list()
        for bag in bags:
            jumlah = len(BagItem.objects.filter(bag_id = bag.pk))
            d = {
                'pk': bag.pk,
                'number': bag.number,
                'jumlah' : jumlah,
                'user_url': reverse('core-bagging-list-item',
                                    kwargs={ 'bag_id': bag.pk}),
                'action': bag.pk,
            }
            data.append(d)

        response = { 'success': 0, 'data': data }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 

class BaggingListItemApi(View):
    def get(self, request):
        print('bag id : ' + request.GET['bag_id'])
        items = BagItem.objects.filter(bag_id=request.GET['bag_id'])

        data = list()
        for item in items:
            u = {
                'awb-number': item.awb.number,
                'action': item.pk,
            }
            data.append(u)

        response = { 'success': 0, 'data': data }
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
        bag_number_list = []
        bag_id_list=[]
        awb_list = []
        print("shipment id : " + request.POST['shipment_id']) 
        runsheet = Shipment.objects.filter(
                transportation_id=request.POST['shipment_id']).update(received_by = user.fullname, received_at = datetime.now(), destination = user.site.address)

        for item in request.POST.getlist('awb_list'):
            if item.startswith('BAG'):
                bag_number_list.append(item)
            else:
                awb_list.append(item)

        try:
            bag_id_qs = Bag.objects.filter(number__in=bag_number_list)
            for bag in list(bag_id_qs):
                bag_id_list.append(bag.id)

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
        print("shipment id : " + request.POST['shipment_id'])
        print("smu : " + request.POST['smu'])
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

        if not request.POST.get('courier_id', False) \
            and not request.POST.get('forwarder_id', False):
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
        if not request.POST.get('courier_id', False):
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

            ItemSite.objects.filter(
                                site_id=user.site.id,
                                awb_id__in=awb_id_list).update(
                                item_status_id=status.id)
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


# user_id, awb, status_code,
# receiver_name, receive_date
class ItemDeliveryUpdateApi(View):
    def post(self, request):
        if not request.POST['user_id'] \
                or not request.POST['data']:
            response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
            return HttpResponse(json.dumps(response),
                        content_type='application/json')

        
        data_list = json.loads(request.POST['data'])
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


        

        status_qs = ItemStatus.objects.filter(code__in=['WC','FW'])
        status_delivery_id = []
        for status in list(status_qs):
            status_delivery_id.append(status.id)

        try:
            for data_dict in data_list:
                self.update_delivery(data_dict)
           
            
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
       
    def update_delivery(self, data_dict):
        awb = AWB.objects.get(data_dict['awb'])
        if data_dict['status_code'] is 'SC' \
                or data_dict['status_code'] is 'OK':
            Delivery.objects.filter(site_id=user.site.id, 
                                    awb_id=awb.id,
                                    status_id__in=status_delivery_id) \
                            .update(status_id=delivery_status.id,
                                    receiver_name=data_dict['receiver_name'],
                                    receive_date=self.convert_to_datetime(
                                        data_dict['receive_date']))
            awb.status_id=delivery_status.id
            awb.save()
            ItemSite.objects.filter(site_id=user.site.id,
                                        item_status_id=status.id,
                                        awb_id=awb.id) \
                            .update(item_status_id=delivery_status.id)
            
            History(awb_id=awb.id, 
                    status=delivery_status.name \
                            + ' [' + data_dict['receiver_name'] + ' at ' \
                            + data_dict['receive_date'] + ']').save()
                
        else:
            fail_status = ItemStatus.objects.get(code=data_dict['status_code'])
            Delivery.objects.filter(site_id=user.site.id, 
                                    awb_id=awb.id,
                                    status_id__in=status_delivery_id) \
                            .update(status_id=fail_status.id)
            awb.status_id=delivery_status.id
            awb.save()
            ItemSite.objects.filter(site_id=user.site.id,
                                        item_status_id=status.id,
                                        awb_id=awb.id) \
                                .update(item_status_id=fail_status.id)

            History(awb_id=awb.id, 
                    status=fail_status.name).save()


    # format date in string: Sep 1 2016  1:33PM
    def convert_to_datetime(self, date_in_string):
        return datetime.strptime(date_in_string, '%b %d %Y %I:%M%p')
        
class PickUpReadApi(View):
    def get(self, request):
        agents = Site.objects.all()
        data = list()
        pu_id = AWB.objects.get(code="PU")
        print ("pick up status id : " + pu_id.id)
        for agent in agents:
            # get item which status is PU (Pick Up)
            items = ItemSite.objects.filter(site=agent.id).filter(awb_id=pu_id.id)
            t = {
                'name': agent.name,
                'type': agent.type.name,
                'address': agent.address,
                'city': agent.city.name,
                'amount':len(items),
            }
            data.append(t)

        response = { 'success':0, 'data': data}
        return HttpResponse(json.dumps(response), content_type='application/json')

class ManifestingListApi(View):
    def get(self, request):
        data = list()
        item_shipments = Shipment.objects.all()
        for item_shipment in item_shipments:
            items = ItemShipment.objects.filter(shipment_id=item_shipment.id)
            bags = ItemBagShipment.objects.filter(shipment_id=item_shipment.id)
            d = {
                'shipment_id':item_shipment.id,
                'employee': item_shipment.sent_by,
                'origin_site': item_shipment.origin_site.name,
                'destination_site': item_shipment.destination_site.name,
                'transportation': item_shipment.transportation.identifier,
                'bagamount': len(bags),
                'itemamount': len(items),
            }
            data.append(d)

        response = {
            'success': 0,
            'data': data,
        }

        return HttpResponse(json.dumps(response), content_type='application/json')

class AirportListApi(View):
    def get(self, request):
        data = list()
        shipments = Shipment.objects.all()
        for shipment in shipments:
            transportations = Transportation.objects.filter(id = shipment.transportation.id, transportation_type = 2)
            for transportation in transportations :
                d = {
                    'plane_id': shipment.id,
                    'plane_identifier': transportation.identifier,
                    'origin_city': transportation.origin_city.name,
                    'departed_at': transportation.departed_at.strftime('%Y/%m/%d %H:%M:%S'),
                    'destination_city': transportation.destination.name,
                    'arrived_at': transportation.arrived_at.strftime('%Y/%m/%d %H:%M:%S'),
                    'base': transportation.base,
                    'smu' : shipment.smu,
                    'operator': transportation.operator,
                }
                data.append(d)

        response = {
            'success': 0,
            'data': data,
        }
 
        return HttpResponse(json.dumps(response), content_type='application/json')

class TransportationReadApi(View):
    def get(self, request):
        transportations = Transportation.objects.all()
        data = list()
        for transportation in transportations:
            t = {
                'transportation_type': transportation.transportation_type.name,
                'transportation_type_pk': transportation.transportation_type_id,
                'identifier': transportation.identifier,
                'operator': transportation.operator,
                'base': transportation.base,
                'origin_city': transportation.origin_city.name,
                'origin_pk': transportation.origin_city_id,
                'destination_city': transportation.destination.name,
                'destination_pk': transportation.destination_id,
                'capacity': transportation.capacity,
                'action': transportation.pk,
            }
            data.append(t)

        response = { 'success': 0, 'data': data }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 

class TransportationCreateApi(View):
    def post(self, request):
        if not request.POST['transportation_type'] \
                or not request.POST['operator'] \
                or not request.POST['identifier'] \
                or not request.POST['origin_city'] \
                or not request.POST['destination_city']:
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # TODO error handling when site already exists
        # write to database
        try:
            s = Transportation(origin_city_id=int(request.POST['origin_city']),
                       destination_id=int(request.POST['destination_city']),
                       transportation_type_id=int(request.POST['transportation_type']),
                       identifier=request.POST['identifier'],
                       capacity=request.POST['capacity'],
                       base=request.POST['base'],
                       operator=request.POST['operator'])
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

class TransportationUpdateApi(View):
    def post(self, request):
        if not request.POST['pk'] \
                or not request.POST['transportation_type'] \
                or not request.POST['origin_city'] \
                or not request.POST['destination_city'] \
                or not request.POST['operator'] \
                or not request.POST['identifier'] :
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # TODO error handling when site already exists
        # write to database
        try:
            t = Transportation.objects.get(pk=request.POST['pk'])
        except Site.DoesNotExist:
            response = {
                'success': -1,
                'message': "Fail to update",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        try:
            t.origin_city_id = int(request.POST['origin_city'])
            t.destination_id = int(request.POST['destination_city'])
            t.transaction_type_id = int(request.POST['transportation_type'])
            t.identifier = request.POST['identifier']
            t.base = request.POST['base']
            t.operator = request.POST['operator']
            t.capacity = request.POST['capacity']
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

class TransportationDeleteApi(View):
    def post(self, request):
        try:
            transportation = Transportation.objects.get(pk=self.request.POST['pk'])
            transportation.delete()
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

class CourierReadApi(View):
    def get(self, request):
        couriers = Courier.objects.all()
        data = list()
        for courier in couriers:
            t = {
                'transportation_type': courier.transportation_type.name,
                'transportation_type_pk': courier.transportation_type_id,
                'fullname': courier.name,
                'phone': courier.phone,
                'city': courier.city.name,
                'city_pk': courier.city_id,
                'action': courier.pk,
            }
            data.append(t)

        response = { 'success': 0, 'data': data }
        return HttpResponse(json.dumps(response),
                            content_type='application/json') 

class CourierCreateApi(View):
    def post(self, request):
        if not request.POST['transportation_type'] \
                or not request.POST['fullname'] \
                or not request.POST['phone'] \
                or not request.POST['city'] :
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # TODO error handling when site already exists
        # write to database
        try:
            s = Courier(city_id=int(request.POST['city']),
                       transportation_type_id=int(request.POST['transportation_type']),
                       name=request.POST['fullname'],
                       phone=request.POST['phone']
                )
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

class CourierUpdateApi(View):
    def post(self, request):
        if not request.POST['pk'] \
                or not request.POST['fullname'] \
                or not request.POST['phone'] \
                or not request.POST['transportation_type'] \
                or not request.POST['city'] :
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # TODO error handling when site already exists
        # write to database
        try:
            t = Courier.objects.get(pk=request.POST['pk'])
        except Site.DoesNotExist:
            response = {
                'success': -1,
                'message': "Fail to update",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        try:
            t.city_id = int(request.POST['city'])
            t.transaction_type_id = int(request.POST['transportation_type'])
            t.fullname = request.POST['fullname']
            t.phone = request.POST['phone']
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

class CourierDeleteApi(View):
    def post(self, request):
        try:
            courier = Courier.objects.get(pk=self.request.POST['pk'])
            courier.delete()
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

class BagCreateApi(View):
    def post(self, request):
        if not request.POST['number'] :
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # TODO error handling when site already exists
        # write to database
        try:
            s = Bag(number=request.POST['number'],
                )
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

class BagUpdateApi(View):
    def post(self, request):
        if not request.POST['pk'] \
                or not request.POST['number'] :
            response = {
                'success': -1,
                'message': "Parameters are not complete",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        # TODO error handling when site already exists
        # write to database
        try:
            t = Bag.objects.get(pk=request.POST['pk'])
        except Site.DoesNotExist:
            response = {
                'success': -1,
                'message': "Fail to update",
            }
            return HttpResponse(json.dumps(response),
                                content_type='application/json') 

        try:
            t.number = request.POST['number']
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

class BagDeleteApi(View):
    def post(self, request):
        try:
            bag = Bag.objects.get(pk=self.request.POST['pk'])
            bag.delete()
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


