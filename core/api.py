from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import DatabaseError, transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import View

import simplejson as json

from account.models import CustomUser
from core.models import History, Item, ItemSite, ItemStatus, Site, Tariff, \
                        Shipment, ItemShipment
from core.logics import generate_awb


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

# required user_id, awb
class OutboundApi(View):
    
    @transaction.atomic
    def post(self, request):
        if not request.POST['user_id'] \
                or not request.POST['awb']:
                    response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
                    return HttpResponse(json.dumps(response),
                                        content_type='application/json')
        # retrieve location
        user = CustomUser.objects.get(pk=request.POST['user_id'])
        location = Site.objects.get(pk=user.site.id)
        collected_status = ItemStatus.objects.get(name__iexact='COLLECTED')
        shipping_status = ItemStatus.objects.get(name__iexact='ON SHIPPING')

        item = Item.objects.get(awb__iexact=request.POST['awb'])

        # update item_shipment
        item_shipment = ItemShipment.objects.get(item_id=item.id)
        item_shipment.item_shipment_status_id=shipping_status.id
        item_shipment.save()


        # update item_site
        item_site = ItemSite.objects.get(item_id=item.id)
        item_site.item_status_id = collected_status.id
        item_site.updated_at = timezone.now()
        item_site.save()

       
        #insert to History
        history = History(
                    item_id=item.id,
                    status=shipping_status.name)

        history.save()

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                                        content_type='application/json')



# required user_id, awb, rack_id
class InboundApi(View):
    
    @transaction.atomic
    def post(self, request):
        if not request.POST['user_id'] \
                or not request.POST['awb']:
                    response = {
                        'success': -1,
                        'message': "Parameters are not complete",
                    }
                    return HttpResponse(json.dumps(response),
                                        content_type='application/json')
        # retrieve location
        user = CustomUser.objects.get(pk=request.POST['user_id'])
        location = Site.objects.get(pk=user.site.id)
        shipped_status = ItemStatus.objects.get(name__iexact='SHIPPED')

        item = Item.objects.get(awb__iexact=request.POST['awb'])
        
        item_site_status = ItemStatus.objects.get(name__iexact='ON TRANSIT')
        
        #if location.city.id == item.sender_city.id:
        #    item_site_status = ItemStatus.objects.get(name__iexact='MANIFESTED')
        #if location.city.id == item.receiver_city.id:
        #    item_site_status = ItemStatus.objects.get(name__iexact='RECEIVED ON DESTINATION')

        # update item_shipment
        item_shipment = ItemShipment.objects.get(item_id=item.id)
        item_shipment.item_shipment_status_id=shipped_status.id
        item_shipment.save()


        # insert item_site
        item_site = ItemSite(
                        item_id=item.id,
                        site_id=user.site.id,
                        rack_id=request.POST['rack_id'],
                        received_at=timezone.now(),
                        received_by=user.fullname
                    )
                        

        item_site.item_storage_status_id=item_site_status.id
        item_site.save()



       
        #insert to History
        history = History(
                    item_id=item.id,
                    status=shipped_status.name)

        history.save()

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                                        content_type='application/json')


class InsertItemApi(View):

    @transaction.atomic
    def post(self, request):

        # retrieve location
        user = CustomUser.objects.get(pk=request.POST['user_id'])
        location = Site.objects.get(pk=user.site_id)
        # TODO still hardcode
        status_to_be_collected = ItemStatus.objects.get(name__iexact='TO BE COLLECTED')
        
        #create item
        item = Item(
                user_id=user.id,
                awb=self.generate_awb(location.id),
                sender_name=request.POST['sender_name'],
                sender_address=request.POST['sender_address'],
                sender_zip_code=request.POST['sender_zip_code'],
                receiver_name=request.POST['receiver_name'],
                receiver_address=request.POST['receiver_address'],
                receiver_zip_code=request.POST['receiver_zip_code'],
                good_name=request.POST['good_name'])

        item.sender_city_id=int(request.POST['sender_city_id']),
        item.receiver_city_id=int(request.POST['receiver_city_id']),
        item.status_id=status_to_be_collected.id
        item.save()

        #insert to item_site
        item_site = ItemSite(
                        item_id=item.id,
                        site_id=location.id,
                        rack_id= request.POST['rack_id'],
                        received_at=timezone.now(),
                        received_by=user.fullname)
                        

        item_site.item_storage_status_id=status_to_be_collected.id
        item_site.save()

        #insert to History
        history = History(
                    item_id=item.id,
                    status=status_to_be_collected.name)

        history.save()
        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                                        content_type='application/json')

    def generate_random(self):
        number = ''
        for i in range(8):
            number += random.choice(string.digits)
        return number

    def generate_awb(self, site_id):
        return 'LOGH' + str(site_id).zfill(4) + self.generate_random()


# required params: user_id, transportation_id, cost
class RunsheetApi(View):

    @transaction.atomic
    def post(self, request):
        staff = CustomUser.objects.get(pk=request.POST['user_id'])

        # TODO still hardcode
        status_to_be_collected = ItemStatus.objects.get(name__iexact='TO BE COLLECTED')
        
        
        print 'city id : ' + str(staff.site.city_id)
        # retrieve same city agent
        agent_qs = Site.objects.filter(Q(city_id=staff.site.city_id) &
                        (Q(type__name='Agen') | Q(type__name='Sub Agen')))
         
        
        agent_sites = []
        for agent in agent_qs.iterator():
            agent_sites.append(agent.id)


        # collect items
        item_to_collect = ItemSite.objects.filter(
                Q(item_status_id=status_to_be_collected.id) &
                Q(site_id=agent.id))
        
        if not item_to_collect.exists():
            response = {
                'success': -1,
                'message': 'No item to collect'
                
            }
            return HttpResponse(json.dumps(response),
                                        content_type='application/json')

        # TODO need mechanism to check whether runsheet has been generated 
        #       to avoid staff to generate DOUBLE runsheet

        # generate runsheet
        runsheet = Shipment(
                    cost=request.POST['cost'],
                    transportation_id=request.POST['transportation_id'])

        runsheet.origin_site = staff.site

        runsheet.destination_site = staff.site
        runsheet.save()
        
        # TODO mechanism to generate bag id
        bag_id = 'BAG0001'

        # insert item_shipment
        for item_site in item_to_collect.iterator():
            ItemShipment.objects.create(
                    item_id=item_site.item_id,
                    shipment=runsheet,
                    bag_id=bag_id,
                    item_shipment_status=status_to_be_collected)

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                                        content_type='application/json')
