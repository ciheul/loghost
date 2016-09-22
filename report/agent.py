import copy
from datetime import datetime, timedelta, time as tiime
import os
from StringIO import StringIO

from django.http import HttpResponse
from django.conf import settings

from core.models import Item

import barcode
from barcode.writer import ImageWriter

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape, LEGAL
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, SimpleDocTemplate, Table, TableStyle
from reportlab.platypus.flowables import Image, Spacer
from reportlab.platypus.paragraph import Paragraph


class AgentReport:
    def print_awb2(self, request):
        item = Item.objects.get(pk=request.POST['pk'])

        barcode_path = self.generate_barcode(item.awb)

        # setting for sending back the PDF in response
        filename = 'awb.pdf'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="%s"' % filename

        # pdf instance
        buff = StringIO()
        doc = SimpleDocTemplate(buff, pagesize=A4, leftMargin=40,
                                topMargin=30, rightMargin=40,
                                bottomMargin=40)
        doc.pagesize = landscape(A4)

        # style
        stylesheet = getSampleStyleSheet()

        # datetime style on the top-right page
        datetime_style = copy.deepcopy(stylesheet['Normal'])
        datetime_style.alignment = TA_RIGHT

        normal_style = copy.deepcopy(stylesheet['Normal'])
        # normal_style.alignment = TA_CENTER

        # title style
        title = 'CONSIGNMENT NOTE'
        title_style = stylesheet['Title']

        # flowables
        elements = []

        ##### LOGO #####
        # insert Axes logo into flowables
        img_path = os.path.join(settings.BASE_DIR,
                                'static/loghost/images/area-51-logistik.png')
        img_reader = ImageReader(img_path)
        img_width, img_height = img_reader.getSize()

        data = open(img_path)
        img_io = StringIO(data.read())
        img = Image(img_io, width=img_width/2, height=img_height/2)
        img.hAlign = 'LEFT'

        ea = elements.append

        # elements.append(Spacer(0, 10))
        elements.append(img)
        elements.append(Spacer(0, 10))

        elements.append(Paragraph(title, title_style))

        current_time = datetime.now().strftime('%d-%m-%Y  %H:%M:%S')
        elements.append(Paragraph(current_time, normal_style))
        elements.append(Spacer(0, 10))

        data = [
            ['Kota Asal', ': ' + item.sender_city.name, '', 'Kota Tujuan', ': ' + item.receiver_city.name],
            ['Pembayaran', ': ' + item.payment_type.name],
        ]
        t = Table(data, hAlign='LEFT')
        elements.append(t)

        elements.append(Spacer(0, 20))

        ea(Paragraph('<b>Pengirim</b> : ' + item.sender_name.upper(), normal_style))
        ea(Paragraph(item.sender_address.upper(), normal_style))
        ea(Paragraph(item.sender_city.name.upper(), normal_style))

        sender_zip_code = item.sender_zip_code.upper() \
            if item.sender_zip_code else ''
        ea(Paragraph('Kode Pos : ' + sender_zip_code, normal_style))

        sender_phone = item.sender_phone if item.sender_phone else ''
        ea(Paragraph('Telepon : ' + sender_phone, normal_style))

        elements.append(Spacer(0, 10))

        ea(Paragraph('<b>Penerima</b> : ' + item.receiver_name.upper(), normal_style))
        ea(Paragraph(item.receiver_address.upper(), normal_style))
        ea(Paragraph(item.receiver_city.name.upper(), normal_style))

        receiver_zip_code = item.receiver_zip_code.upper() \
            if item.receiver_zip_code else ''
        ea(Paragraph('Kode Pos : ' + receiver_zip_code, normal_style))

        receiver_phone = item.receiver_phone if item.receiver_phone else ''
        ea(Paragraph('Telepon : ' + receiver_phone, normal_style))

        elements.append(Spacer(0, 10))

        good_name = item.good_name.upper() if item.good_name else ''
        ea(Paragraph('Barang: ' + good_name, normal_style))

        good_value = item.good_value if item.good_value else ''
        ea(Paragraph('Nilai barang: ' + good_value, normal_style))

        instruction = item.instruction.upper() if item.instruction else ''
        ea(Paragraph('Instruksi: ' + instruction, normal_style))

        information = item.information.upper() if item.information else ''
        ea(Paragraph('Keterangan: ' + information, normal_style))

        elements.append(Spacer(0, 30))

        ##### LOGO #####
        # insert Axes logo into flowables
        img_path = os.path.join(settings.BASE_DIR, barcode_path)
        print img_path
        img_reader = ImageReader(img_path)
        img_width, img_height = img_reader.getSize()

        data = open(img_path)
        img_io = StringIO(data.read())
        img = Image(img_io, width=img_width/3, height=img_height/3)
        img.hAlign = 'LEFT'

        # elements.append(Spacer(0, 20))
        elements.append(img)
        elements.append(Spacer(0, 40))

        footer_left = """
            Dokumen ini dicetak secara otomatis dengan Area 51 online \
            system.<br/>
            Untuk pengecekan status kirim silakan mengunjungi \
            www.area51logistik.com.
        """

        ea(Paragraph(footer_left, normal_style))

        # build the PDF
        doc.build(elements)

        # write it to response
        response.write(buff.getvalue())

        buff.close()

        # os.remove(path)

        return response

    def print_awb(self, request):
        item = Item.objects.get(pk=request.POST['pk'])

        # setting for sending back the PDF in response
        filename = 'awb.pdf'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="%s"' % filename

        barcode_path = self.generate_barcode(item.awb.number)

        c = canvas.Canvas(response, pagesize=landscape(A4))

        ##### LOGO #####
        # insert Axes logo into flowables
        img_path = os.path.join(settings.BASE_DIR,
                                'static/loghost/images/area-51-logistik.png')
        c.drawImage(img_path, 30, 490, mask='auto')

        c.drawString(240, 550, "Jalan Pondok Gede Raya No. 48D")
        c.drawString(240, 535, "Pondok Gede Jakarta Timur")
        c.drawString(240, 520, "Telepon: 021 - 2298 4551 / 021 - 2298 4669")
        c.drawString(240, 505, "Web : www.area51logistik.com")
        c.drawString(240, 490, "Email : info@area51logistik.com")

        ##### BARCODE #####
        img_reader = ImageReader(barcode_path)
        img_width, img_height = img_reader.getSize()
        c.drawImage(barcode_path, 580, 430,
                    width=img_width/2, height=img_height/2, mask='auto')

        c.drawString(30, 430, "Kota Asal : " + item.sender_city.name)
        c.drawString(250, 430, "Kota Tujuan : " + item.receiver_city.name)
        c.drawString(30, 415, "Pembayaran : " + item.payment_type.name)

        ##### SENDER #####
        c.drawString(30, 380, "Pengirim : " + item.sender_name.upper())
        c.drawString(30, 365, item.sender_address.upper())
        c.drawString(30, 350, item.sender_city.name.upper())

        sender_zip_code = item.sender_zip_code.upper() \
            if item.sender_zip_code else ''
        c.drawString(30, 335, "Kode Pos : " + sender_zip_code)

        sender_phone = item.sender_phone if item.sender_phone else ''
        c.drawString(30, 320, "Telepon : " + sender_phone)

        ##### RECEIVER #####
        c.drawString(30, 280, "Penerima: " + item.receiver_name.upper())
        c.drawString(30, 265, item.receiver_address.upper())
        c.drawString(30, 250, item.receiver_city.name.upper())

        receiver_zip_code = item.receiver_zip_code.upper() \
            if item.receiver_zip_code else ''
        c.drawString(30, 235, "Kode Pos : " + receiver_zip_code)

        receiver_phone = item.receiver_phone if item.receiver_phone else ''
        c.drawString(30, 220, "Telepon : " + receiver_phone)

        ##### ADDITIONAL INFORMATIO #####
        good_name = item.good_name.upper() if item.good_name else ''
        c.drawString(350, 380, "Nama Barang: " + item.good_name.upper())

        good_value = item.good_value \
            if item.good_value and item.good_value != 0 else ''
        c.drawString(350, 365, "Nilai Barang: " + good_value)

        instruction = item.instruction.upper() if item.instruction else ''
        c.drawString(350, 350, "Instruksi: " + instruction)

        information = item.information.upper() if item.information else ''
        c.drawString(350, 335, "Information: " + information)

        c.drawString(350, 280, "Berat %11s" % str(item.weight))
        c.drawString(350, 265, "Panjang %7s" % str(item.length))
        c.drawString(350, 250, "Lebar %11s" % str(item.width))
        c.drawString(350, 235, "Tinggi %10s" % str(item.height))
        c.drawString(350, 220, "Jumlah %7s" % str(item.quantity))
        
        c.drawString(600, 380, "No. AWB : " + item.awb.number)
        c.drawString(600, 365, "Layanan : " + item.tariff.service.name)
        c.drawString(600, 350, "Jenis Kiriman : " + item.good_type.name.upper())
        c.drawString(600, 280, "Biaya Kirim : (IDR) %11s" % str('{:,}'.format(item.price)))
        c.drawString(600, 265, "Biaya Lain-lain : (IDR) %10s" % '0') 
        c.drawString(600, 250, "Total Biaya : (IDR) %11s" % str('{:,}'.format(item.price))) 

        c.drawString(650, 170, "Diterima") 
        c.drawString(600, 100, "(%45s" % ')') 

        c.drawString(80, 110, "Dokumen ini dicetak menggunakan sistem online Area 51 secara otomatis") 
        c.drawString(50, 95, "untuk mengetahui status paket Anda, mohon mengunjungi web www.area51logistik.com.") 

        c.showPage()
        c.save()

        return response


    def generate_barcode(self, awb):
        ean = barcode.get('ean13', awb, writer=ImageWriter())

        # write barcode in png format to dist and return its path
        path = ean.save(awb)

        return path
