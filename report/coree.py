from datetime import datetime
import os

from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.units import cm, mm, inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

from core.models import Bag, BagItem, Item, ItemShipment, ItemBagShipment, Shipment

class Report:
    def __init__(self):
        self.page_width, self.page_height = A4
        self.n_style = ParagraphStyle(name='normal',
                                      spaceAfter=50,
                                      fontSize=6,
                                      fontName='Helvetica')

    def run(self):
        response = HttpResponse(content_type='appication/pdf')
        response['Content-Disposition'] = 'filename="blankform.pdf"'

        c = canvas.Canvas(response, pagesize=A4)
        
        self.generate(c)
        c.showPage()
        c.save()

        return response

    def coord(self, x, y, unit=1):
        # x, y = x*unit, self.page_height - y*unit
        return x, y

    def generate(self, c):
        c.translate(cm, cm)

        # logo
        logo_path = 'report/images/area-51-logistik.png'
        logo_reader = ImageReader(logo_path)
        logo_width, logo_height = logo_reader.getSize()

        c.drawImage(logo_path, 0, 750,
                    width=logo_width/2,
                    height=logo_height/2, mask='auto')

        # agent information
        c.setFont('Helvetica-Bold', 6)
        c.drawString(100, 780, "AREA 51 JAKARTA")
        c.setFont('Helvetica', 6)
        c.drawString(100, 772, "JALAN PONDOK GEDE RAYA NO. 48D")
        c.drawString(100, 764, "JAKARTA TIMUR")
        c.drawString(100, 756, "Telepon: (021) 2298-4551 / (021) 2298-4669")
        c.drawString(100, 748, "www.area51logistik.com")

        # title
        c.setFont('Helvetica-Bold', 7)
        c.drawCentredString(self.page_width/2, 790,
                            "e-CONSIGNMENT NOTE (e-connote)")

        # time
        c.setFont('Helvetica', 6)
        now = datetime.now()
        c.drawString(300, 780,
                            now.strftime('%Y/%m/%d %H:%M:%S'))

        c.setFont('Helvetica', 6)
        c.drawString(300, 772, "Layanan :")

        c.setFont('Helvetica', 6)
        c.drawString(300, 748, 'Jenis Kiriman :')

        c.setFont('Helvetica', 6)
        c.drawString(450, 748, 'Stempel :')

        # a list of items and their metrics
        data = [
            ['Keterangan', 'Jml', 'Berat', '' , 'Dimensi', '' , 'Berat' ],
            [''          , ''   , 'Asli' , 'L', 'H'      , 'W', 'Volume'],
        ]
        col_widths = (20*mm, 10*mm, 10*mm, 10*mm, 10*mm, 10*mm, 10*mm)

        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            # align for header
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            # align for body 
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))

        table.wrapOn(c, 50, 50)
        table.drawOn(c, *self.coord(300, 718, mm))

        # sender and receiver
        data = [
            ['Kota Asal'    , ':', 'Kota Tujuan', ':'],
            ['No. Pelanggan', ':', 'Pembayaran' , ':'],
        ]

        table = Table(data, colWidths=(20*mm, 30*mm, 15*mm, 20*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(0, 715, mm))

        c.setFont('Helvetica', 6)
        sender_info = "<b>Pengirim</b> :"
        sender = Paragraph(sender_info, self.n_style)
        sender.wrapOn(c, self.page_width, self.page_height)
        sender.drawOn(c, *self.coord(0, 695, mm))
 
        c.setFont('Helvetica', 6)
        c.drawString(0, 665, 'Attn :')

        data = [
                ['Kode Pos', ':'],
                ['Telepon' , ':'],
        ]
         
        table = Table(data, colWidths=(10*mm, 30*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(165, 670, mm))

        receiver_info = "<b>Penerima</b> :"
        receiver = Paragraph(receiver_info, self.n_style)
        receiver.wrapOn(c, self.page_width, self.page_height)
        receiver.drawOn(c, *self.coord(0, 647, mm))
 
        c.setFont('Helvetica', 6)
        c.drawString(0, 613, 'Attn :')

        data = [
                ['Kode Pos', ':'],
                ['Telepon' , ':'],
        ]

        table = Table(data, colWidths=(10*mm, 30*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(165, 615, mm))

        data = [
            ['Instruksi Khusus', ' :'          ],
            ['Catatan'         , ' :'          ],
            ['Nilai Barang'    , ' :'          ],
            ['Stempel'         , ' :'          ],
        ]

        table = Table(data, colWidths=(20*mm, 30*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(0, 570, mm))

        data = [
            ['Jumlah', ':'],
            ['',''],
            ['Biaya Kirim', ':'],
            ['Biaya Lain-lain', ':'],
            ['Asuransi', ':'],
            ['Adm. Asuransi', ':'],
            ['Total Biaya', ':'],
        ]

        table = Table(data, colWidths=(20*mm, 30*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(300, 630, mm))

        data = [
            ['Berat', ':'],
        ]

        table = Table(data, colWidths=(10*mm, 30*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(450, 686, mm))

        c.setFont('Helvetica', 6)
        c.drawCentredString(350, 610, 'Petugas')
         
        c.setFont('Helvetica', 6)
        c.drawCentredString(460, 610, 'Ttd. Pengirim')
          
        c.setFont('Helvetica', 6)
        c.drawCentredString(460, 580, '(                         )')
        
        c.setFont('Helvetica', 6)
        c.drawCentredString(350, 580, '(                         )')
        
        c.setFont('Helvetica-Bold', 5)
        c.drawCentredString(self.page_width/4, 560, 'Dokumen ini dicetak secara otomatis dengan "AREA 51 online system"')

        c.setFont('Helvetica-Bold', 4)
        c.drawCentredString(self.page_width/4, 554, 'untuk pengecekan status kiriman silakan mengunjungi www.area51logistik.com')

        c.setFont('Helvetica-Bold', 5)
        c.drawCentredString(self.page_width/1.45, 560, 'Dengan menandatangani e-connote ini pengirim telah membaca, memahami dan sepakat untuk')
        c.drawCentredString(self.page_width/1.45, 554, 'terikat dengan Syarat Standar Pengiriman (SSP). PT. Area 51 Logistik yang tercantum dalam') 
        c.drawCentredString(self.page_width/1.45, 548, 'halaman 2 (dua) yang merupakan satu kesatuan tidak terpisahkan dari e-connote ini.')

class ManifestReport:
    def __init__(self):
        self.page_width, self.page_height = A4
        self.n_style = ParagraphStyle(name='normal', spaceAfter=50, fontSize=6, fontName='Helvetica')

    def run(self, shipment_pk):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="RunSheet.pdf"'

        c = canvas.Canvas(response, pagesize=A4)
        
        self.generate(c, shipment_pk)
        c.showPage()
        c.save()

        return response

    def coord(self, x, y, unit=1):
        # x, y = x*unit, self.page_height - y*unit
        return x, y

    def generate(self, c, shipment_pk):
        shipment = Shipment.objects.get(pk = shipment_pk)
        item_shipments = ItemShipment.objects.filter(shipment_id = shipment_pk)
        bag_shipments = ItemBagShipment.objects.filter(shipment_id = shipment_pk)
        c.translate(cm, cm)

        #logo
        logo_path = 'report/images/area-51-logistik.png'
        logo_reader = ImageReader(logo_path)
        logo_width, logo_height = logo_reader.getSize()

        c.drawImage(logo_path, 0, 750, width = logo_width/2, height = logo_height/2, mask='auto')

        # agent information
        c.setFont('Helvetica-Bold', 8)
        c.drawCentredString(self.page_width/2, 790, "AREA 51 JAKARTA")
        c.setFont('Helvetica', 8)
        c.drawCentredString(self.page_width/2, 782, "JALAN PONDOK GEDE RAYA No. 48D")

        c.setFont('Helvetica-Bold', 9)
        c.drawCentredString(self.page_width/2, 765, "INWARD CARGO MANIFEST FOR VESSEL UNDER")
        c.setFont('Helvetica-Bold', 9)
        c.drawCentredString(self.page_width/2, 753, "FIVE TONS, FERRY, TRAIN, CAR, VEHICLE, ETC.")

        c.setFont('Helvetica', 8)
        c.drawCentredString(self.page_width/2, 735, "Some Number")

        c.setFont('Helvetica', 6)
        c.drawString(430, 780, "Form Approved:")

        c.setFont('Helvetica', 7)
        c.drawString(430, 773, "Some Number")

        data = [
            ['Customs Manifest/ Out Bond Number'],
            ["" + str(shipment.id)],
            ['Page No.'],
        ]
        col_widths = (38.4*mm)

        table = Table(data, colWidths=col_widths, rowHeights=4*mm)
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('LINEABOVE', (0, -1), (-1, -1), 0, colors.black),
        ]))

        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(430, 730, mm))
        
        data = [
                ['1. Detail Pengiriman', '2. Petugas : ' + '' + shipment.sent_by],
                ['3. Nama dan Alamat Perusahaan : ' +  shipment.origin_site.name + ', ' + shipment.origin_site.address, '4. Alamat Stasiun Keberangkatan: ' + shipment.origin_site.city.name],
                ['5. Alamat Stasiun Tujuan : ' + shipment.destination_site.city.name, '6. Tanggal Pemberangkatan : ' + shipment.sent_at.strftime('%Y/%m/%d %H:%M:%S')],
        ]
        col_widths = (95*mm, 95*mm)

        table = Table(data, colWidths=col_widths, rowHeights=12*mm)
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ]))

        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(0, 628, mm))

        itemsstring = ''
        itemsdata = ''
        bagsstring = ''
        for bag_shipment in bag_shipments:
            bags = Bag.objects.filter(id = bag_shipment.bag.id)
            for bag in bags:
                bagsdata = ''
                bagscode = ''
                bagitems = BagItem.objects.filter(bag_id = bag.id)
                bagscode = 'Kode Bag :' + bag.number + '\n'
                for bagitem in bagitems :
                    items = Item.objects.get(awb_id = bagitem.awb.id)
                    itemsdata = '    Kode Barang :' + bagitem.awb.number + \
                    ',\n    Nama Barang : ' + items.good_name + \
                    ',\n    Weight : ' + (str(int(items.weight)) if items.weight else '0') + \
                    'kg, Height : ' + (str(int(items.height)) if items.height else '0') + \
                    'cm, Length : ' + (str(int(items.length)) if items.length else '0') + \
                    'cm, Width : ' + (str(int(items.width)) if items.width else '0') + 'cm \n'
                    bagsdata = bagsdata + itemsdata
                bagsdata = bagscode + bagsdata
                bagsstring = bagsstring + bagsdata
        
        for item_shipment in item_shipments :
            items = Item.objects.get(awb_id = item_shipment.awb.id)
            itemsdata = 'Kode Bag : - ' + \
            '\nKode Barang :' + item_shipment.awb.number + \
            ',\nNama Barang : ' + items.good_name + \
            ',\nWeight : ' + (str(int(items.weight)) if items.weight else '0') + \
            'kg, Height : ' + (str(int(items.height)) if items.height else '0') + \
            'cm, Length : ' + (str(int(items.length)) if items.length else '0') + \
            'cm, Width : ' + (str(int(items.width)) if items.width else '0') + 'cm\n \n'
            itemsstring = itemsstring + itemsdata

        finalstring = bagsstring + '\n' + itemsstring

        data = [
            ['Column No. 1', 'Column No.2', 'Column No.3', 'Column No.4'],
            ['Alamat Penerima', 'Nomor Kendaraan', 'List Barang', 'Keterangan'],
            ['' + shipment.destination_site.address, '' + shipment.transportation.identifier, \
            finalstring, ''],
     
        ]
        col_widths = (35*mm, 25*mm, 95*mm, 35*mm)
        row_heights = (5*mm, 5*mm, 130*mm)

        table = Table(data, colWidths=col_widths, rowHeights=row_heights)
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('VALIGN', (0, 2), (-1, 2), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 2), (-1, 2), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ]))

        table.wrapOn(c, 30, 30)
        table.drawOn(c, *self.coord(0, 231, mm))

        c.setFont('Helvetica-Bold',10)
        c.drawCentredString(self.page_width/2, 218, "CARRIER'S CERTIFICATE")

        c.setFont('Helvetica', 8)
        c.drawString(0, 205, "Kepada Koordinator / Supervisor Stasiun Kedatangan:")

        c.setFont('Helvetica', 8)
        c.drawString(0, 190, "Kurir yang bertugas dengan ini menyatakan bahwa ________________________________________________________________________________")

        c.setFont('Helvetica', 8)
        c.drawString(0, 175, "Adalah pemilik / penerima barang dari barang-barang yang disebutkan di atas.")

        
        c.setFont('Helvetica',8)
        c.drawString(80, 150, "Saya menyatakan bahwa semua yang tercantum pada lembar manifest ini adalah benar sesuai dengan kondisi di lapangan.")

        c.setFont('Helvetica',8)
        c.drawString(80, 125, "Tanggal ____________________. Koordinator / Kurir yang bertugas _________________________________________")

        c.setFont('Helvetica-Oblique',6)
        c.drawString(400, 116, "(Signature)")

if __name__ == '__main__':
    r = Report()
    r.run()
