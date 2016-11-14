from django.test import TestCase

from account.models import CustomUser
from core.models import AWB, Bag, City, Courier, ItemStatus, SiteType, Site, GoodType, Service, PaymentType, Tariff, Transportation, TransportationType

import simplejson
import json

# Create your tests here.

class AgentShipmentApiTest(TestCase):
    def setUp(self):
        # available AWB
        AWB.objects.create(number="CGK1234567890")
        AWB.objects.create(number="CGK1234567891")

        # initial item status
        ItemStatus.objects.create(code="SD", name="Shipment Detail Entry")
        ItemStatus.objects.create(code="PR", name="Processed")
        ItemStatus.objects.create(code="OB", name="Outbound")
        ItemStatus.objects.create(code="AF", name="Arrive at Facility")
        ItemStatus.objects.create(code="WC", name="With Courier")
        ItemStatus.objects.create(code="UL", name="Uplifting")
        ItemStatus.objects.create(code="OK", name="Delivered")
        ItemStatus.objects.create(code="PU", name="Pick Up")

        # initial bag
        Bag.objects.create(number="BAG1234", capacity=3)
        
        # core city
        City.objects.create(name="Jakarta")
        City.objects.create(name="Cilacap")

        # core type
        SiteType.objects.create(name="Kantor Cabang")

        # core Site
        Site.objects.create(name="CV. Test Indah", address="Jakarta", city_id=1, type_id=1)
        Site.objects.create(name="CV. Test Tujuan Indah", address="Cilacap", city_id=2, type_id=1)

        # Core Employee
        self.user = CustomUser.objects.create_user(password="avishena", fullname="avi", email="avishena@loghost.io", site_id=1)

        # Initial Good Type
        GoodType.objects.create(name="Parcel")

        # initial service
        Service.objects.create(name="Express")

        # initial Payment Type
        PaymentType.objects.create(name="Cash")
    
        # initial Tariff
        Tariff.objects.create(price=18000, duration="1-2", destination_id=2, origin_id=1, service_id=1)

        # initial Transportation Type
        TransportationType.objects.create(name="Truck")
        TransportationType.objects.create(name="Flight")

        # initial Transportation
        Transportation.objects.create(identifier='Truck123', base='Jakarta', operator='Trucker', capacity=3, destination_id=2, origin_city_id=1, transportation_type_id=1)
        Transportation.objects.create(identifier="Flight123", base="Jakarta", operator="Flighter", capacity=3, destination_id=2, origin_city_id=1, transportation_type_id=2)

        # initial Courier
        Courier.objects.create(name="Avi", phone="01234567890", transportation_type_id=1, city_id=2)

    def TestShipmentPickUpEntry(self):
        self.client.login(email='avishena@loghost.io', password='avishena')
        response = self.client.post('/agent/api/agent/item/create/',
                data = {'user_id' : 1, 'sender_name' : 'Avi', 'sender_address' : 'Bandung', 'receiver_name' : 'Shena', 'receiver_address' : 'Cilacap', 'receiver_city' : 2, 'sender_city' : 1, 'service' : 1, 'good_type' : 1, 'payment_type' : 1, 'good_name' : 'Buku', 'price' : '18000', 'weight' : '', 'length' : '', 'width' : '', 'height' : '', 'good_value' : '', 'sender_zip_code': '', 'receiver_zip_code' : '', 'sender_phone' : '081234567890', 'receiver_phone' : '082345678901', 'note' : '', 'instruction' : ''},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)
       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awb'), "CGK1234567890")
        self.assertEqual(content.get('awbstatus'), 'PU')
    
    def TestShipmentPickUpEntry2(self):
        self.client.login(email='avishena@loghost.io', password='avishena')
        response = self.client.post('/agent/api/agent/item/create/',
                data = {'user_id' : 1, 'sender_name' : 'Avi', 'sender_address' : 'Bandung', 'receiver_name' : 'Shena', 'receiver_address' : 'Cilacap', 'receiver_city' : 2, 'sender_city' : 1, 'service' : 1, 'good_type' : 1, 'payment_type' : 1, 'good_name' : 'Buku', 'price' : '18000', 'weight' : '', 'length' : '', 'width' : '', 'height' : '', 'good_value' : '', 'sender_zip_code': '', 'receiver_zip_code' : '', 'sender_phone' : '081234567890', 'receiver_phone' : '082345678901', 'note' : '', 'instruction' : ''},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)
       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awb'), "CGK1234567891")
        self.assertEqual(content.get('awbstatus'), 'PU')
    

    def TestShipmentDetailEntry(self):
        self.client.login(email='avishena@loghost.io', password='avishena')
        response = self.client.post('/core/api/item/create/',
                data = {'user_id' : 1, 'sender_name' : 'Avi', 'awb' : 'CGK1234567890', 'sender_address' : 'Bandung', 'receiver_name' : 'Shena', 'receiver_address' : 'Cilacap', 'receiver_city' : 2, 'sender_city' : 1, 'service' : 1, 'good_type' : 1, 'payment_type' : 1, 'good_name' : 'Buku', 'price' : '18000', 'weight' : '', 'length' : '', 'width' : '', 'height' : '', 'good_value' : '', 'sender_zip_code': '', 'receiver_zip_code' : '', 'sender_phone' : '081234567890', 'receiver_phone' : '082345678901', 'note' : '', 'instruction' : ''},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)
       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awb'), "CGK1234567890")
        self.assertEqual(content.get('awbbefore'), 'PU')
        self.assertEqual(content.get('awbstatus'), 'SD')
    
    def TestShipmentDetailEntry2(self):
        self.client.login(email='avishena@loghost.io', password='avishena')
        response = self.client.post('/core/api/item/create/',
                data = {'user_id' : 1, 'sender_name' : 'Avi', 'awb' : 'CGK1234567891', 'sender_address' : 'Bandung', 'receiver_name' : 'Shena', 'receiver_address' : 'Cilacap', 'receiver_city' : 2, 'sender_city' : 1, 'service' : 1, 'good_type' : 1, 'payment_type' : 1, 'good_name' : 'Buku', 'price' : '18000', 'weight' : '', 'length' : '', 'width' : '', 'height' : '', 'good_value' : '', 'sender_zip_code': '', 'receiver_zip_code' : '', 'sender_phone' : '081234567890', 'receiver_phone' : '082345678901', 'note' : '', 'instruction' : ''},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)
       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awb'), "CGK1234567891")
        #self.assertEqual(content.get('awbbefore'), 'PU')
        self.assertEqual(content.get('awbstatus'), 'SD')


    def TestBagging(self):
        response = self.client.post('/core/api/bagging/',
                data = {'user_id' : 1, 'bag_number' : 'BAG1234', 'awb_list' : ['CGK1234567890', 'CGK1234567891']},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['AF', 'AF'])
        self.assertEqual(content.get('awbstatus'), ['PR', 'PR'])
    
    def TestOutbound(self):
        response = self.client.post('/core/api/outbound/',
                data = {'user_id' : 1, 'transportation_id' : 2, 'bag_id_list' : 'BAG1234', 'destination_id': 2},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['PR', 'PR'])
        self.assertEqual(content.get('awbstatus'), ['OB', 'OB'])

    def TestUplifting(self):
        response = self.client.post('/core/api/runsheet/update/',
                data = {'user_id' : 1, 'shipment_id' : 1, 'smu' : 'SMUFlight123'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['OB', 'OB'])
        self.assertEqual(content.get('awbstatus'), ['UL', 'UL'])

    def TestInbound(self):
        response = self.client.post('/core/api/inbound/',
                data = {'user_id' : 1, 'awb_list' : ['CGK1234567890', 'CGK1234567891'], 'transportation_id': 2},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['PU', 'PU'])
        self.assertEqual(content.get('awbstatus'), ['AF', 'AF'])

    def TestInboundDestination(self):
        response = self.client.post('/core/api/inbound/',
                data = {'user_id' : 1, 'awb_list' : 'BAG1234', 'transportation_id': 2},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['UL', 'UL'])
        self.assertEqual(content.get('awbstatus'), ['AF', 'AF'])


    def TestDelivery(self):
        response = self.client.post('/core/api/delivery/create/',
                data = {'user_id' : 1, 'awb_list' : ['CGK1234567890', 'CGK1234567891'], 'courier_id' : 1},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['AF', 'AF'])
        self.assertEqual(content.get('awbstatus'), ['WC', 'WC'])

    def TestDeliveryUpdate(self):
        data = [{'status' : 'OK', 'awb' : 'CGK1234567890', 'receiver_name' : 'Avi', 'receive_date' : '10/10/2016'}, {'status' : 'OK', 'awb' : 'CGK1234567891', 'receiver_name' : 'Avi', 'receive_date' : '10/11/2016'}]        
        response = self.client.post('/core/api/delivery/update/',
                data = {
                    'user_id' : 1,
                    'data' : json.dumps(data),
                    'status_code' : 'OK'
                },
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['WC', 'WC'])
        self.assertEqual(content.get('awbstatus'), ['OK', 'OK'])

    def test_case(self):
        self.TestShipmentPickUpEntry()
        self.TestShipmentPickUpEntry2()
        self.TestInbound()
        self.TestBagging()
        self.TestOutbound()
        self.TestUplifting()
        self.TestInboundDestination()
        self.TestDelivery()
        self.TestDeliveryUpdate()

class AgentMultipleShipmentApiTest(TestCase):
    def setUp(self):
        # available AWB
        AWB.objects.create(number="CGK1234567890")
        AWB.objects.create(number="CGK1234567891")
        AWB.objects.create(number="CGK1234567892")
        AWB.objects.create(number="CGK1234567893")
        AWB.objects.create(number="CGK1234567894")

        # initial item status
        ItemStatus.objects.create(code="SD", name="Shipment Detail Entry")
        ItemStatus.objects.create(code="PR", name="Processed")
        ItemStatus.objects.create(code="OB", name="Outbound")
        ItemStatus.objects.create(code="AF", name="Arrive at Facility")
        ItemStatus.objects.create(code="WC", name="With Courier")
        ItemStatus.objects.create(code="UL", name="Uplifting")
        ItemStatus.objects.create(code="OK", name="Delivered")
        ItemStatus.objects.create(code="PU", name="Pick Up")

        # initial bag
        Bag.objects.create(number="BAG1234", capacity=3)
        
        # core city
        City.objects.create(name="Jakarta")
        City.objects.create(name="Cilacap")
        City.objects.create(name="Bandung")
        City.objects.create(name="Purwokerto")
        City.objects.create(name="Ciamis")
        City.objects.create(name="Jogja")

        # core type
        SiteType.objects.create(name="Kantor Cabang")

        # core Site
        Site.objects.create(name="CV. Test Indah", address="Jakarta", city_id=1, type_id=1)
        Site.objects.create(name="CV. Test Tujuan Indah", address="Cilacap", city_id=2, type_id=1)

        # Core Employee
        self.user = CustomUser.objects.create_user(password="avishena", fullname="avi", email="avishena@loghost.io", site_id=1)

        # Initial Good Type
        GoodType.objects.create(name="Parcel")

        # initial service
        Service.objects.create(name="Express")

        # initial Payment Type
        PaymentType.objects.create(name="Cash")
 
        # initial Tariff
        Tariff.objects.create(price=18000, duration="1-2", destination_id=2, origin_id=1, service_id=1)
        Tariff.objects.create(price=18000, duration="1-2", destination_id=3, origin_id=1, service_id=1)
        Tariff.objects.create(price=18000, duration="1-2", destination_id=4, origin_id=1, service_id=1)
        Tariff.objects.create(price=18000, duration="1-2", destination_id=5, origin_id=1, service_id=1)
        Tariff.objects.create(price=18000, duration="1-2", destination_id=6, origin_id=1, service_id=1)

        # initial Transportation Type
        TransportationType.objects.create(name="Truck")
        TransportationType.objects.create(name="Flight")

        # initial Transportation
        Transportation.objects.create(identifier='Truck123', base='Jakarta', operator='Trucker', capacity=3, destination_id=2, origin_city_id=1, transportation_type_id=1)
        Transportation.objects.create(identifier="Flight123", base="Jakarta", operator="Flighter", capacity=3, destination_id=2, origin_city_id=1, transportation_type_id=2)

        # initial Courier
        Courier.objects.create(name="Avi", phone="01234567890", transportation_type_id=1, city_id=2)

    def TestShipmentPickUpEntry(self):
        self.client.login(email='avishena@loghost.io', password='avishena')
        response = self.client.post('/agent/api/agent/item/create/multi/',
                data = {'user_id' : 1, 'sender_name' : ['Avi', 'Avi', 'Avi', 'Avi', 'Avi'], 'awb' : '', 'sender_address' : ['Bandung', 'Bandung', 'Bandung', 'Bandung', 'Bandung'], 'receiver_name' : ['Bias', 'Sekar', 'Avi', 'Shena', 'Aoi'], 'receiver_address' : ['Cilacap', 'Bandung', 'Purwokerto', 'Ciamis', 'Jogja'], 'receiver_city' : [2, 3, 4, 5, 6], 'sender_city' : [1, 1, 1, 1, 1], 'service' : [1, 1, 1, 1, 1], 'good_type' : [1, 1, 1, 1, 1], 'payment_type' : [1, 1, 1, 1, 1], 'good_name' : ['Buku', 'Buku', 'Buku', 'Buku', 'Buku'], 'price' : ['18000', '18000', '18000', '18000', '18000'], 'weight' : ['', '', '', '', ''], 'length' : ['', '', '', '', ''], 'width' : ['', '', '', '',''], 'height' : ['', '', '', '', ''], 'good_value' : [0, 0, 0, 0, 0], 'sender_zip_code': ['', '', '', '', ''], 'receiver_zip_code' : ['', '', '', '', ''], 'sender_phone' : ['081234567890', '081234567891', '081234567892', '081234567893', '081234567894'], 'receiver_phone' : ['082345678901', '082345678902', '082345678903', '082345678904', '082345678905'], 'information' : ['', '', '', '', ''], 'instruction' : ['', '', '', '', '']},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)
       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awb'), ["CGK1234567890", "CGK1234567891", "CGK1234567892", "CGK1234567893", "CGK1234567894"])
        self.assertEqual(content.get('id'), [1,2,3,4,5])
        self.assertEqual(content.get('awbstatus'), ['PU', 'PU', 'PU', 'PU', 'PU'])

    def TestShipmentDetailEntry(self):
        self.client.login(email='avishena@loghost.io', password='avishena')
        response = self.client.post('/core/api/item/create/multi/',
                data = {'user_id' : 1, 'sender_name' : ['Avi', 'Avi', 'Avi', 'Avi', 'Avi'], 'awb' : ['CGK1234567890', 'CGK1234567891', 'CGK1234567892', 'CGK1234567893', 'CGK1234567894'], 'sender_address' : ['Bandung', 'Bandung', 'Bandung', 'Bandung', 'Bandung'], 'receiver_name' : ['Bias', 'Sekar', 'Avi', 'Shena', 'Aoi'], 'receiver_address' : ['Cilacap', 'Bandung', 'Purwokerto', 'Ciamis', 'Jogja'], 'receiver_city' : [2, 3, 4, 5, 6], 'sender_city' : [1, 1, 1, 1, 1], 'service' : [1, 1, 1, 1, 1], 'good_type' : [1, 1, 1, 1, 1], 'payment_type' : [1, 1, 1, 1, 1], 'good_name' : ['Buku', 'Buku', 'Buku', 'Buku', 'Buku'], 'price' : ['18000', '18000', '18000', '18000', '18000'], 'weight' : ['', '', '', '', ''], 'length' : ['', '', '', '', ''], 'width' : ['', '', '', '',''], 'height' : ['', '', '', '', ''], 'good_value' : [0, 0, 0, 0, 0], 'sender_zip_code': ['', '', '', '', ''], 'receiver_zip_code' : ['', '', '', '', ''], 'sender_phone' : ['081234567890', '081234567891', '081234567892', '081234567893', '081234567894'], 'receiver_phone' : ['082345678901', '082345678902', '082345678903', '082345678904', '082345678905'], 'information' : ['', '', '', '', ''], 'instruction' : ['', '', '', '', '']},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)
       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awb'), ["CGK1234567890", "CGK1234567891", "CGK1234567892", "CGK1234567893", "CGK1234567894"])
        self.assertEqual(content.get('id'), [6, 7, 8, 9, 10])        
        self.assertEqual(content.get('awbbefore'), ['PU', 'PU', 'PU', 'PU', 'PU'])
        self.assertEqual(content.get('awbstatus'), ['SD', 'SD', 'SD', 'SD', 'SD'])

    def TestBagging(self):
        response = self.client.post('/core/api/bagging/',
                data = {'user_id' : 1, 'bag_number' : 'BAG1234', 'awb_list' : ['CGK1234567890', 'CGK1234567891']},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['AF', 'AF'])
        self.assertEqual(content.get('awbstatus'), ['PR', 'PR'])
        print('Test Bagging Done')

    def TestOutbound(self):
        response = self.client.post('/core/api/outbound/',
                data = {'user_id' : 1, 'transportation_id' : 2, 'bag_id_list' : 'BAG1234', 'awb_list' : ['CGK1234567892', 'CGK1234567893', 'CGK1234567894'],'destination_id': 2},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['PR', 'PR', 'AF', 'AF', 'AF'])
        self.assertEqual(content.get('awbstatus'), ['OB', 'OB', 'OB', 'OB', 'OB'])
        print('Test Outbound Done')

    def TestUplifting(self):
        response = self.client.post('/core/api/runsheet/update/',
                data = {'user_id' : 1, 'shipment_id' : 1, 'smu' : 'SMUFlight123'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['OB', 'OB', 'OB', 'OB', 'OB'])
        self.assertEqual(content.get('awbstatus'), ['UL', 'UL', 'UL', 'UL', 'UL'])
        print('Test Uplifting Done')

    def TestInbound(self):
        response = self.client.post('/core/api/inbound/',
                data = {'user_id' : 1, 'awb_list' : ['CGK1234567890', 'CGK1234567891', 'CGK1234567893', 'CGK1234567894', 'CGK1234567892'], 'transportation_id': 2},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['PU', 'PU', 'PU', 'PU', 'PU'])
        self.assertEqual(content.get('awbstatus'), ['AF', 'AF', 'AF', 'AF', 'AF'])
        print('Test Inbound Done')

    def TestInboundDestination(self):
        response = self.client.post('/core/api/inbound/',
                data = {'user_id' : 1, 'awb_list' : ['BAG1234', 'CGK1234567893', 'CGK1234567894', 'CGK1234567892'], 'transportation_id': 2},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['UL', 'UL', 'UL', 'UL', 'UL'])
        self.assertEqual(content.get('awbstatus'), ['AF', 'AF', 'AF', 'AF', 'AF'])
        print('Test Inbound Done')


    def TestDelivery(self):
        response = self.client.post('/core/api/delivery/create/',
                data = {'user_id' : 1, 'awb_list' : ['CGK1234567890', 'CGK1234567891', 'CGK1234567892', 'CGK1234567893', 'CGK1234567894'], 'courier_id' : 1},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['AF', 'AF', 'AF', 'AF', 'AF'])
        self.assertEqual(content.get('awbstatus'), ['WC', 'WC', 'WC', 'WC', 'WC'])
        print('Test Delivery Done')

    def TestDeliveryUpdate(self):
        data = [
                {'status' : 'OK', 'awb' : 'CGK1234567890', 'receiver_name' : 'Avi', 'receive_date' : '10/10/2016'}, 
                {'status' : 'OK', 'awb' : 'CGK1234567891', 'receiver_name' : 'Avi', 'receive_date' : '10/11/2016'},
                {'status' : 'OK', 'awb' : 'CGK1234567892', 'receiver_name' : 'Avi', 'receive_date' : '10/11/2016'},
                {'status' : 'OK', 'awb' : 'CGK1234567893', 'receiver_name' : 'Avi', 'receive_date' : '10/11/2016'},
                {'status' : 'OK', 'awb' : 'CGK1234567894', 'receiver_name' : 'Avi', 'receive_date' : '10/11/2016'}
                ]        
        response = self.client.post('/core/api/delivery/update/',
                data = {
                    'user_id' : 1,
                    'data' : json.dumps(data),
                    'status_code' : 'OK'
                },
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('success'), 0)
        self.assertEqual(content.get('awbbefore'), ['WC', 'WC', 'WC', 'WC', 'WC'])
        self.assertEqual(content.get('awbstatus'), ['OK', 'OK', 'OK', 'OK', 'OK'])
        print('Test Delivery Update')

    def test_case(self):
        self.TestShipmentPickUpEntry()
        self.TestInbound()
        self.TestBagging()
        self.TestOutbound()
        self.TestUplifting()
        self.TestInboundDestination()
        self.TestDelivery()
        self.TestDeliveryUpdate()


