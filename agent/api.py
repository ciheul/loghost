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
                        ItemBagShipment, Incident, Transportation, Delivery
from core.logics import generate_awb

import traceback, random, string

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

        sd_item_status = ItemStatus.objects.get(code__exact='PU')

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

class AgentItemCreateMultiApi(View):
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

