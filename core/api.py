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
                        Shipment, ItemShipment, AWB, Bag, BagItem
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

        location = Site.objects.get(pk=user.site.id)
        collected_status = ItemStatus.objects.get(name__iexact='COLLECTED')
        shipping_status = ItemStatus.objects.get(name__iexact='ON SHIPPING')

        item = None
        try:
            item = Item.objects.get(awb__iexact=request.POST['awb'])
        except:
            response = {
                    'success': -1,
                    'message': "Item not found"
                    }
            return HttpResponse(json.dumps(response),
                                content_type='application/json')


        try:
            # update item_shipment
            item_shipment = ItemShipment.objects.get(
                    Q(item_id=item.id) &
                    Q(shipment__origin_site_id=user.site.id))
            item_shipment.item_shipment_status_id_id=shipping_status.id
            item_shipment.save()


            # update item_site
            item_site = ItemSite.objects.get(
                Q(item_id=item.id) &
                Q(site_id=user.site.id))
            item_site.item_status_id = collected_status.id
            item_site.updated_at = timezone.now()
            item_site.save()

       
            #insert to History
            history = History(
                        item_id=item.id,
                        status=collected_status.name)

            history.save()
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



class ItemOnProcess(View):
    def post(self, request):
        if not request.POST['user_id'] \
            or not request.POST['awb'] :
                response = {
                    'success': -1,
                    'message': "Parameters are not complete",
                }
                return HttpResponse(json.dumps(response),
                        content_type='application/json')

        try:
            on_process_status = ItemStatus.objects.get(code='OP')
            # update awb
            awb = AWB.objects.get(number=request.POST['awb'])
            awb.status_id=on_process_status.id
            awb.save()
            # update itemsite
            item_site = ItemSite.objects.get(awb_id=awb.id)
            item_site.status_id=on_process_status.id
            item_site.save()
            # insert history
            History(awb_id=awb.id, status=on_process_status.name).save()
        except:
            print traceback.format_exc()
            
            # return error response
            response = {
                'success': -1,
                'message': 'Database problem'
                }

        
        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')


class ItemProcessed(View):
    def post(self, request):
        if not request.POST['user_id'] \
            or not request.POST['awb'] :
                response = {
                    'success': -1,
                    'message': "Parameters are not complete",
                }
                return HttpResponse(json.dumps(response),
                        content_type='application/json')

        try:
            processed_status = ItemStatus.objects.get(code='PR')
            #update status awb
            awb = AWB.objects.get(number=request.POST['awb'])
            awb.status_id=processed_status.id
            awb.save()
            #update status item site
            item_site = ItemSite.objects.get(awb_id=awb.id)
            item_site.status_id=processed_status.id
            item_site.save()
            # insert history
            History(awb_id=awb.id, status=processed_status.name).save()
        except:
            print traceback.format_exc()
            
            # return error response
            response = {
                'success': -1,
                'message': 'Database problem'
                }

        
        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')


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
        try:
            for item in request.POST.getlist('awb_list'):
                #update awb
                awb = AWB.objects.get(number__iexact=item)
                awb.status_id = processed_status.id
                awb.save()
                #insert bag_item
                bag_item = BagItem(bag_id=bag.id, awb_id=awb.id)
                bag_item.save()
                #update item_site
                item_site = ItemStatus.objects.get(awb_id=awb.id)
                item_site.status_id=processed_status.id
                item_site.save()
                # insert history
                History(awb_id=awb.id, status=processed_status.name).save()
                
        except:
            print traceback.format_exc()
            
            # return error response
            response = {
                'success': -1,
                'message': 'Database problem'
                }

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')


            

class InboundBulkApi(View):
    
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
        
        for item in awb_list:
            if item.startswith('BAG'):
                bag_id_list.append(item, arrived_status.id, user)
            else:
                awb_list.append(item, arrived_status.id, user)
        
        try:
            self.update_status_items(awb_list)
            self.update_status_item_on_bags(bag_id_list)
        except:
            print 
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


    def update_status_items(self, awb_list, status_id, user):
        for item in awb_list:
           self.update_status_item(item, status_id, user)

    def update_status_item_on_bags(self, bag_id_list, status_id, user):
        for bag_id in bag_id_list:
            bag_item_qs = BagItem.objects.filter(bag_id=bag_id)
            for bag_item in bag_item_qs.iterator():
                self.update_status_item_by_id(bag_item.awb_id, status_id, user)

    def update_status_item_by_id(self, awb_id, status_id, user):
        awb = AWB.objects.get(pk=awb_id)
        awb.status_id = status_id
        awb.save()

        item = ItemSite(
                awb_id=awb_id,
                site_id=user.site.id,
                received_at=timezone.now(),
                received_by=user.fullname)
        item.save()

    def update_status_item(self, awb_number, status_id, user):
        awb = AWB.objects.get(number=awb_number)
        awb.status_id = status_id
        awb.save()

        item = ItemSite(
                awb_id=awb_id,
                site_id=user.site.id,
                received_at=timezone.now(),
                received_by=user.fullname)
        item.save()


class InsertItemApi(View):

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

#    def generate_random(self):
#        number = ''
#        for i in range(8):
#            number += random.choice(string.digits)
#        return number

#    def generate_awb(self, site_id):
#        return 'LOGH' + str(site_id).zfill(4) + self.generate_random()


# required params: user_id, transportation_id, cost
class RunsheetApi(View):

    def post(self, request):
        staff = CustomUser.objects.get(pk=request.POST['user_id'])

        # TODO still hardcode
        status_to_be_collected = ItemStatus.objects.get(name__iexact='TO BE COLLECTED')
        
        
        # retrieve same city agent
        agent_qs = Site.objects.filter(Q(city_id=staff.site.city_id) &
                        (Q(type__name='Agen') | Q(type__name='Sub Agen')))
         
        
        # no agent to collect
        if not agent_qs:
            response = {
                'success': -1,
                'message': 'No agent to collect'
                
            }
            return HttpResponse(json.dumps(response),
                                        content_type='application/json')

        #example : {'agent_id':'query_set_item_to_be_collect'}
        agent_items = {}
        for agent in agent_qs.iterator():
            item_to_collect = ItemSite.objects.filter(
                Q(item_status_id=status_to_be_collected.id) &
                Q(site_id=agent.id))
            if not item_to_collect:
                continue
            agent_items.update({agent.id : item_to_collect})

        # no item to collect
        if not agent_items:
            response = {
                'success': -1,
                'message': 'No item to collect'
                
            }
            return HttpResponse(json.dumps(response),
                                        content_type='application/json')

        # TODO need mechanism to check whether runsheet has been generated 
        #       to avoid staff to generate DOUBLE runsheet

        # generate for every agent / site
        for site_id, item_qs in agent_items.items():
            # create runsheet
            runsheet = Shipment(
                        cost=request.POST['cost'],
                        transportation_id=request.POST['transportation_id'])
            runsheet.origin_site_id = site_id
            runsheet.destination_site = staff.site
            runsheet.save()
        
            # TODO mechanism to generate bag id
            bag_id = 'BAG0001'

            # insert item_shipment
            for item_site in item_qs.iterator():
                ItemShipment.objects.create(
                        item_id=item_site.item_id,
                        shipment=runsheet,
                        bag_id=bag_id,
                        item_shipment_status_id=status_to_be_collected)

        # return response
        response = {
            'success': 0
            }
        return HttpResponse(json.dumps(response),
                content_type='application/json')


class ProcessingApi(View):

    def post(self, request):
        staff = CustomUser.objects.get(pk=request.POST['user_id'])
        manifested_status = ItemStatus.objects.get(name__iexact='MANIFESTED')
        processed_status = ItemStatus.objects.get(name__iexact='ON PROCESS')
        status_to_be_collected = ItemStatus.objects.get(name__iexact='TO BE COLLECTED')


        item = None
        try:
            item = Item.objects.get(awb__iexact=request.POST['awb'])
        except:
            response = {
                    'success': -1,
                    'message': "Item not found"
                    }
            return HttpResponse(json.dumps(response),
                                content_type='application/json')

        try:
            # create runsheet
            runsheet = Shipment(
                        cost=request.POST['cost'],
                        transportation_id=request.POST['transportation_id'])
            runsheet.origin_site_id = staff.site.id
            runsheet.destination_site_id = item.receiver_city_id
            runsheet.save()
            
            # TODO mechanism to generate bag id
            bag_id = 'BAG0001'

            # insert item_shipment
            ItemShipment.objects.create(
                    item_id=item.id,
                    shipment=runsheet,
                    bag_id=bag_id,
                    item_shipment_status_id=status_to_be_collected)

            # update status of item site
            item_site = ItemSite.objects.get(Q(item_id=item.id) &
                            Q(site_id=staff.site.id ) &
                            Q(item_status_id=manifested_status))

            item_site.item_status_id=processed_status
            item_site.save()

            # update history
            history = History(
                        item_id=item.id,
                        status=processed_status.name)
            history.save()

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
