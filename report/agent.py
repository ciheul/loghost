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
from reportlab.lib.units import cm, mm, inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Image, SimpleDocTemplate, Table, TableStyle
from reportlab.platypus.flowables import Image, Spacer
from reportlab.platypus.paragraph import Paragraph


class AgentReport:
    def __init__(self):
        self.page_width, self.page_height = A4
        self.n_style = ParagraphStyle(name='normal',
                                      spaceAfter=50,
                                      fontSize=6,
                                      fontName='Helvetica')
        self.sender_style = ParagraphStyle(name='sender',
                                           fontSize=8,
                                           fontName='Helvetica')
        self.receiver_style = ParagraphStyle(name='receiver',
                                             spaceAfter=10,
                                             fontSize=16,
                                             fontName='Helvetica-Bold')
        self.statement_style = ParagraphStyle(name='statement',
                                              fontSize=8,
                                              fontName='Helvetica')
        self.styles = getSampleStyleSheet()

    def generate_barcode(self, awb):
        ean = barcode.get('ean13', awb, writer=ImageWriter())

        # write barcode in png format to dist and return its path
        path = ean.save(awb)

        return path

    def coord(self, x, y, unit=1):
        # x, y = x*unit, self.page_height - y*unit
        return x, y

    # USELESS
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

        barcode_path = self.generate_barcode(item.awb)

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
        
        c.drawString(600, 380, "No. AWB : " + item.awb)
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

    def print_shipment_marking(self, request):
        AWB_NUMBER = 12345
        DESTINATION = 'BANYUWANGI'
        SERVICE = 'EXPRESS'
        PAYMENT_TYPE = 'PREPAID CASH'
        PICKUP_AT = '2016/09/22 14:30'
        GOOD_NAME = "Buku-Buku Pelajaran"
        PCS = '2'
        TOTAL = '4'
        WEIGHT = "750 Kg"
        VOL_WEIGHT = "1230 Kg"

        sender = list()
        sender.append(Paragraph('PT Matra Integra Intika', self.sender_style))
        sender.append(Paragraph('Wisma Metropol, Lt 26', self.sender_style))
        sender.append(Paragraph('Jl. Masjid Kav 31-32', self.sender_style))
        sender.append(Paragraph('Jakarta, 12320', self.sender_style))
        sender.append(Paragraph('Telp: 2334000', self.sender_style))
        sender.append(Paragraph('Name: Andi Surya', self.sender_style))

        receiver = list()
        receiver.append(Paragraph('PT Bank Rakyat Indonesia', self.receiver_style))
        receiver.append(Paragraph('Divisi Kredit Komersial', self.receiver_style))
        receiver.append(Paragraph('Jl. Jendral Sudirman 71', self.receiver_style))
        receiver.append(Paragraph('Banyuwangi, 56320', self.receiver_style))
        receiver.append(Paragraph('Telp: 2523000', self.receiver_style))
        receiver.append(Paragraph('Bp. Wahyu Tunggono', self.receiver_style))

        shipper_reference = list()
        content = "D/N 00021, D/N 00022, D/N 00023, D/N 00024, D/N 00025, D/N 00026, D/N 00027"
        shipper_reference.append(Paragraph(content, self.sender_style))

        # setting for sending back the PDF in response
        filename = 'shipment-marking.pdf'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="%s"' % filename

        # barcode_path = self.generate_barcode(AWB_NUMBER)

        c = canvas.Canvas(response, pagesize=A4)

        # from bottom left, move the origin (0, 0).
        # 1 cm to the right and 1 cm to the top
        # c.translate(cm, cm)

        # rectangle
        c.rect(1*cm, self.page_height/2, self.page_width - 2*cm, self.page_height/2 - 1*cm)

        # no1 horizontal line
        c.line(1*cm, 730, self.page_width - 1*cm, 730)

        # no2 horizontal line
        c.line(8*cm, 665, self.page_width - 1*cm, 665)

        # no3 horizontal line
        c.line(1*cm, 630, self.page_width - 1*cm, 630)

        # no4 horizontal line
        c.line(1*cm, 550, 8*cm, 550)

        # no5 horizontal line
        c.line(1*cm, 490, 8*cm, 490)

        # no6 horizontal line
        c.line(490, 560, self.page_width - 1*cm, 560)

        # no7 horizontal line
        c.line(490, 485, self.page_width - 1*cm, 485)

        # no8 horizontal line
        c.line(1*cm, 470, 490, 470)

        # no9 horizontal line
        c.line(490, 452, self.page_width - 1*cm, 452)

        # no1 vertical line
        c.line(2*cm, 550, 2*cm, 630)

        # no2 vertical line
        c.line(8*cm, self.page_height/2, 8*cm, 730)

        # no3 vertical line
        c.line(490, 630, 490, self.page_height/2)

        # horizontal line in the center page
        # c.line(0, self.page_height/2, self.page_width, self.page_height/2)

        # insert Axes logo into flowables
        img_path = os.path.join(settings.BASE_DIR,
                                'static/loghost/images/area-51-logistik.png')
        img_reader = ImageReader(img_path)
        img_width, img_height = img_reader.getSize()

        c.drawImage(img_path, 85, 427, width=img_width/2, height=img_height/2,
                    mask='auto')

        c.setFont('Helvetica', 8)
        c.drawString(1.5*cm, 795, 'Destination :')

        c.setFont('Helvetica-Bold', 48)
        c.drawString(2*cm, 750, DESTINATION)

        c.setFont('Helvetica-Bold', 40)
        c.drawString(self.page_width/2, 685, SERVICE)

        c.setFont('Helvetica', 8)
        c.drawString(8.3*cm, 650, 'Account No:')

        c.setFont('Helvetica-Bold', 20)
        c.drawString(self.page_width/2 , 640, PAYMENT_TYPE)

        c.setFont('Helvetica', 8)
        c.drawString(35, 538, "Shipper Reference:")

        c.setFont('Helvetica', 8)
        c.drawString(35, 478, "Pick Up:")

        c.setFont('Helvetica-Bold', 8)
        c.drawString(90, 478, PICKUP_AT)

        c.setFont('Helvetica', 8)
        c.drawString(8.3*cm, 615, "Consignee:")

        c.setFont('Helvetica', 8)
        c.drawString(495, 615, "Pcs No:")

        c.setFont('Helvetica-Bold', 48)
        c.drawString(515, 575, PCS)

        c.setFont('Helvetica', 8)
        c.drawString(495, 545, "Of Total:")

        c.setFont('Helvetica-Bold', 48)
        c.drawString(515, 500, TOTAL)

        c.setFont('Helvetica', 8)
        c.drawString(495, 475, "Weight:")

        c.setFont('Helvetica-Bold', 16)
        c.drawString(500, 458, WEIGHT)

        c.setFont('Helvetica', 8)
        c.drawString(495, 443, "Vol. Weight:")

        c.setFont('Helvetica-Bold', 16)
        c.drawString(500, 428, VOL_WEIGHT)

        c.setFont('Helvetica', 8)
        c.drawString(8.3*cm, 455, "Isi:")

        c.setFont('Helvetica-Bold', 12)
        c.drawString(270, 440, GOOD_NAME)

        f = Frame(2.5*cm, 542, 150, 90, showBoundary=0)
        f.addFromList(sender, c)

        f = Frame(235, 480, 245, 125, showBoundary=0)
        f.addFromList(receiver, c)

        f = Frame(30, 490, 190, 50, showBoundary=0)
        f.addFromList(shipper_reference, c)

        c.translate(45, 0)
        c.rotate(90)
        c.setFont('Helvetica', 12)
        c.drawString(20*cm, 0, "Shipper:")
        c.rotate(0)

        c.showPage()
        c.save()

        return response

    def print_shipment_receipt_multiple_address(self, request):
        # setting for sending back the PDF in response
        filename = 'shipment-receipt.pdf'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="%s"' % filename

        c = canvas.Canvas(response, pagesize=A4)

        # HEADER
        # insert Axes logo into flowables
        img_path = os.path.join(settings.BASE_DIR,
                                'static/loghost/images/area-51-logistik.png')
        img_reader = ImageReader(img_path)
        img_width, img_height = img_reader.getSize()

        c.drawImage(img_path, 30, 762, width=img_width * 0.75, height=img_height * 0.75,
                    mask='auto')

        c.setFont('Helvetica-Bold', 16)
        c.drawString(250, 780, 'BUKTI PENERIMAAN KIRIMAN')

        # agent information
        c.setFont('Helvetica', 6)
        c.drawCentredString(100, 748, "JALAN PONDOK GEDE RAYA NO. 48D, JAKARTA TIMUR")
        c.drawCentredString(100, 740, "Telepon: (021) 2298-4551 / (021) 2298-4669")
        c.drawCentredString(100, 732, "www.area51logistik.com")

        # LINE AND RECTANGLE
        # horizontal line in the center page
        c.line(0, self.page_height/2, self.page_width, self.page_height/2)

        # no1 rectangle
        c.rect(20, 660, 270, 60)

        # no2 rectangle
        c.rect(305, 660, 270, 60)

        # no3 rectangle
        c.rect(20, 500, 555, 140)

        # no4 rectangle
        c.rect(20, 430, 350, 63)

        # no5 rectangle
        c.rect(385, 430, 190, 63)

        # no1 horizontal line 
        c.line(20, 620, 575, 620)

        # no2 horizontal line 
        c.line(20, 518, 575, 518)

        # no1 vertical line 
        c.line(40, 640, 40, 500)

        # no2 vertical line 
        c.line(133, 640, 133, 500)

        # no3 vertical line 
        c.line(180, 640, 180, 500)

        # no4 vertical line 
        c.line(235, 640, 235, 500)

        # no5 vertical line 
        c.line(260, 640, 260, 500)

        # no6 vertical line 
        c.line(295, 640, 295, 500)

        # no7 vertical line 
        c.line(335, 640, 335, 500)

        # no8 vertical line 
        c.line(360, 640, 360, 500)

        # no9 vertical line 
        c.line(440, 640, 440, 500)

        # no10 vertical line 
        c.line(500, 640, 500, 500)

        # TEXT
        # sender and receiver
        data = [
            ['Operator'    , ' :', 'No. Pelanggan', ' :'],
            ['Hari/Tanggal', ' :', 'Pengirim'     , ' :'],
            ['Jam'         , ' :', 'Alamat'       , ' :'],
            ['Lokasi'      , ' :', ''             , ''  ],
            ['Kota'        , ' :', ''             , ''  ],
        ]

        table = Table(data, colWidths=(18*mm, 82*mm, 20*mm, 20*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), -1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(27, 665, mm))

        c.setFont('Helvetica', 10)
        c.drawString(25, 645, 'Rincian Barang Kiriman')

        header_y = 627
        c.setFont('Helvetica', 10)
        c.drawString(24, header_y, 'No')
        c.drawString(55, header_y, 'AWB Number')
        c.drawString(138, header_y, 'Layanan')
        c.drawString(190, header_y, 'Tujuan')
        c.drawString(240, header_y, 'Pcs')
        c.drawString(265, header_y, 'Berat')
        c.drawString(300, header_y, 'Brt Vol')
        c.drawString(340, header_y, 'Ins')
        c.drawString(380, header_y, 'Penerima')
        c.drawString(460, header_y, 'Ref.')
        c.drawString(530, header_y, 'Rp.')

        statement= list()
        content = "Dengan ini pengirim menyatakan telah memberi keterangan " \
            "sebenarnya dan menyetujui syarat-syarat pengiriman seperti " \
            "tertera di halaman belakang tanda terima barang kiriman ini."
        statement.append(Paragraph(content, self.statement_style))

        f = Frame(21, 422, 150, 75, showBoundary=0)
        f.addFromList(statement, c)

        c.setFont('Helvetica-Bold', 8)
        c.drawString(270, 480, 'Pengirim,')

        c.setFont('Helvetica', 8)
        c.drawString(190, 435, 'Nama Jelas :')

        c.setFont('Helvetica-Bold', 8)
        c.drawString(460, 480, 'Petugas Penerima,')

        c.setFont('Helvetica', 8)
        c.drawString(400, 435, 'Nama Jelas :')

        c.showPage()
        c.save()

        return response
