from datetime import datetime
import os

from core.models import Item
from core.models import Service
from core.models import Tariff

from django.http import HttpResponse

from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.units import cm, mm, inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

class Report:
    def __init__(self):
        self.page_width, self.page_height = A4
        self.n_style = ParagraphStyle(name='normal',
                                      spaceAfter=50,
                                      fontSize=6,
                                      fontName='Helvetica')

    def run(self, request):
        response = HttpResponse(content_type='appication/pdf')
        response['Content-Disposition'] = 'filename="BTform.pdf"'

        c = canvas.Canvas(response, pagesize=A4)
        
        self.generate(c, request)
        c.showPage()
        c.save()

        return response

    def coord(self, x, y, unit=1):
        # x, y = x*unit, self.page_height - y*unit
        return x, y

    def generate(self, c, request):
        print request.POST
        item = Item.objects.get(pk=request.POST['pk'])

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
        c.drawString(300, 780, now.strftime('%d-%m-%Y %H:%M:%S'))

        c.setFont('Helvetica', 6)
        c.drawString(300, 772, "Layanan : ")

        service = Service.objects.get(pk=item.tariff.id)
        c.setFont('Helvetica', 8)
        c.drawString(305, 760, '' + service.name.upper())

        c.setFont('Helvetica', 6)
        c.drawString(300, 748, 'Jenis Kiriman : ' + item.good_type.name.upper())

        c.setFont('Helvetica', 6)
        c.drawString(450, 748, 'Stempel :')

        # a list of items and their metrics
        data = [
            ['Keterangan', 'Jml', 'Berat', '' , 'Dimensi', '' , 'Berat' ],
            [''          , ''   , 'Asli' , 'L', 'H'      , 'W', 'Volume'],
            ['', item.quantity, item.weight, item.length, item.height, item.width, (item.length * item.height * item.width)],
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
            ['Kota Asal'    , ': ' + item.sender_city.name, 'Kota Tujuan', ': ' + item.receiver_city.name],
            ['No. Pelanggan', ': ', 'Pembayaran' , ': ' + item.payment_type.name],
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
        sender_info = "<b>Pengirim</b> : " + item.sender_name.upper()
        sender = Paragraph(sender_info, self.n_style)
        sender.wrapOn(c, self.page_width, self.page_height)
        sender.drawOn(c, *self.coord(0, 695, mm))

        sender_address = item.sender_address.upper()
        sender = Paragraph(sender_address, self.n_style)
        sender.wrapOn(c, 150, 688)
        sender.drawOn(c, *self.coord(0, 680, mm))
 
        c.setFont('Helvetica', 6)
        c.drawString(0, 665, 'Attn :')

        data = [
                ['Kode Pos', ': ' + str(item.sender_zip_code) if item.sender_zip_code else ':'],
                ['Telepon' , ': ' + str(item.sender_phone) if item.sender_phone else ':'],
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

        receiver_info = "<b>Penerima</b> : " + item.receiver_name.upper()
        receiver = Paragraph(receiver_info, self.n_style)
        receiver.wrapOn(c, self.page_width, self.page_height)
        receiver.drawOn(c, *self.coord(0, 647, mm))
        
        c.setFont('Helvetica', 6)
        receiver_address = item.receiver_address.upper()
        receiver = Paragraph(receiver_address, self.n_style)
        receiver.wrapOn(c, 150, self.page_height)
        receiver.drawOn(c, *self.coord(0, 500, mm))

        c.setFont('Helvetica', 6)
        c.drawString(0, 613, 'Attn :')

        data = [
                ['Kode Pos', ': ' + str(item.receiver_zip_code) if item.receiver_zip_code else ':'],
                ['Telepon' , ': ' + str(item.receiver_phone) if item.receiver_phone else ':'],
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
            ['Instruksi Khusus' , ' : ' + str(item.instruction) if item.instruction else ":"],
            ['Catatan'          , ' : ' + str(item.information) if item.information else ":"],
            ['Nilai Barang'     , ' : ' + str(item.good_value).upper() if item.good_value else ":"],
            ['Keterangan Barang', ' : ' + str(item.good_name).upper() if item.good_name else ":"],
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
                ['Jumlah', ': ' + str(item.quantity) , ''],
            ['', '', ''],
            ['Biaya Kirim', ': IDR ', str(item.price) + '.00'],
            ['Biaya Lain-lain', ': IDR', '0.00'],
            ['Asuransi', ': IDR', '0.00'],
            ['Adm. Asuransi', ': IDR', '0.00'],
            ['Total Biaya', ': IDR', str(item.price) + '.00'],
        ]

        table = Table(data, colWidths=(20*mm, 5*mm, 40*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-2, -1), 0),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(300, 630, mm))

        data = [
                ['Berat', ': ' + str(int(item.weight)) if item.weight else ':'],
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
        c.drawCentredString(350, 580, '( ' + str(item.user.fullname).upper() + ' )')
        month = now.strftime('%b')
        c.drawCentredString(350, 572, now.strftime('%d-'+ month.upper() + '-%Y %H:%M'))

        c.setFont('Helvetica', 6)
        c.drawCentredString(460, 580, '(                         )')
        
        c.setFont('Helvetica-Bold', 5)
        c.drawCentredString(self.page_width/4, 560, 'Dokumen ini dicetak secara otomatis dengan "AREA 51 online system"')

        c.setFont('Helvetica-Bold', 4)
        c.drawCentredString(self.page_width/4, 554, 'untuk pengecekan status kiriman silakan mengunjungi www.area51logistik.com')

        c.setFont('Helvetica-Bold', 5)
        c.drawCentredString(self.page_width/1.45, 560, 'Dengan menandatangani e-connote ini pengirim telah membaca, memahami dan sepakat untuk')
        c.drawCentredString(self.page_width/1.45, 554, 'terikat dengan Syarat Standar Pengiriman (SSP). PT. Area 51 Logistik yang tercantum dalam') 
        c.drawCentredString(self.page_width/1.45, 548, 'halaman 2 (dua) yang merupakan satu kesatuan tidak terpisahkan dari e-connote ini.')


class DeliveryReport:
    def __init__(self):
        self.page_width, self.page_height = A4
        self.n_style = ParagraphStyle(name='normal',
                                      spaceAfter=50,
                                      fontSize=6,
                                      fontName='Helvetica')

    def run(self):
        response = HttpResponse(content_type='appication/pdf')
        response['Content-Disposition'] = 'filename="Delivery.pdf"'

        c = canvas.Canvas(response, pagesize=A4)
        
        self.generate(c)
        c.showPage()
        c.save()

        return response

    def coord(self, x, y, unit=1):
        # x, y = x*unit, self.page_height - y*unit
        return x, y

    def generate(self, c):
        item = Item.objects.get(pk=1)

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
        c.drawCentredString(self.page_width/2, 788,
                            "e-CONSIGNMENT NOTE (e-connote)")

        # time
        c.setFont('Helvetica', 6)
        now = datetime.now()
        c.drawCentredString(self.page_width/2, 772, now.strftime('%d-%m-%Y %H:%M'))
        
        service = Service.objects.get(pk=item.tariff.id)
        c.setFont('Helvetica', 8)
        c.drawCentredString(self.page_width/2, 760, '' + service.name.upper())

        # a list of items and their metrics
        data = [
            ['Keterangan', 'Jml', 'Berat', '' , 'Dimensi', '' , 'Berat' ],
            [''          , ''   , 'Asli' , 'L', 'H'      , 'W', 'Volume'],
            [str(item.information), item.quantity  , item.weight , item.length , item.height, item.weight , (item.length * item.weight * item.height)  ],
        ]
        col_widths = (20*mm, 10*mm, 10*mm, 10*mm, 10*mm, 10*mm, 10*mm)
        table = Table(data, colWidths=col_widths)

        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            # align for header
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(330, 750, mm))

	# price detail
	
	c.setFont('Helvetica', 6)
	c.drawCentredString(350, 675, 'Jumlah :' + str(item.quantity))

	c.setFont('Helvetica', 6)
	c.drawCentredString(450, 675, 'Berat :' + str(int(item.weight)))
	
	data = [
            ['Jenis Kiriman : ','Layanan : '],
	    [item.good_type.name.upper() if item.good_type.name else '', service.name.upper()],
        ]

        table = Table(data, colWidths=(20*mm, 20*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
	    ('ALIGN', (0,-1), (-1, -1), 'LEFT'),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(440, 653, mm))

	data = [
            ['Biaya Kirim', ' : IDR', '' + str(item.price) + '.00'],
            ['Biaya Lain-lain' , ' : IDR', '0.00'],
            ['Asuransi', ' : IDR', '0.00'],
	    ['Adm. Asuransi', ' : IDR', '0.00'],
	    ['Total Biaya', ' : IDR', '' + str(item.price) + '.00']
        ]

        table = Table(data, colWidths=(15*mm, 5*mm, 15*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
	        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
	        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(330, 600, mm))

	data = [
		['Diterima Oleh / Bukti Pengiriman :'],
            	['Pukul' , ' : '],
            	['Tgl', ' : '],
	    	['Nama', ' : '],
        ]

        table = Table(data, colWidths=(15*mm, 10*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
	    ('ALLIGN', (-1, 0), (-1, -1), 'RIGHT'),
	    ('ALLIGN', (0, 0), (0, -1), 'RIGHT'),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(450, 600, mm))
	
        # sender and receiver
        data = [
		    ['Kota Asal'    , ': ' + item.sender_city.name , 'Kota Tujuan', ': ' + item.receiver_city.name],
            ['No. Pelanggan', ': ' +  str(item.id), 'Pembayaran' , ': ' + item.payment_type.name],
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
        sender_info = "<b>Pengirim</b> : " + item.sender_name.upper()
        sender = Paragraph(sender_info, self.n_style)
        sender.wrapOn(c, self.page_width, self.page_height)
        sender.drawOn(c, *self.coord(0, 695, mm))

        sender_address = item.sender_address.upper()
        sender = Paragraph(sender_address, self.n_style)
        sender.wrapOn(c, 150, self.page_height)
        sender.drawOn(c, *self.coord(0, 680, mm))

        data = [
            ['Attn'    , ' : '            ],
	    ['Telepon' , ' : ' + str(item.sender_phone) if item.sender_phone else ':'],
	    ['Kode Pos', ' : ' + str(item.sender_zip_code) if item.sender_zip_code else ':'],
        ]

        table = Table(data, colWidths=(10*mm, 30*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(170, 675, mm))

        receiver_info = "<b>Penerima</b> : " + item.receiver_name.upper()
        receiver = Paragraph(receiver_info, self.n_style)
        receiver.wrapOn(c, self.page_width, self.page_height)
        receiver.drawOn(c, *self.coord(0, 647, mm))

        receiver_address = item.receiver_address.upper()
        receiver = Paragraph(receiver_address, self.n_style)
        receiver.wrapOn(c, 150, self.page_height)
        receiver.drawOn(c, *self.coord(0, 620, mm))

        data = [
            ['Attn'    , ' : '            ],
	    ['Telepon' , ' : ' + str(item.receiver_phone) if item.receiver_phone else ' :'],
	    ['Kode Pos', ' : ' + str(item.receiver_zip_code) if item.receiver_zip_code else ' :'],
        ]

        table = Table(data, colWidths=(10*mm, 30*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(170, 620, mm))

        data = [
            ['Instruksi Khusus', ' : ' + item.instruction.upper() if item.instruction else ' : '],
            ['Keterangan'      , ' : ' + item.good_name.upper() if item.information else ' : '],
            ['Catatan'         , ' : ' + item.information if item.information else ' : '],
            ['Nilai Barang'    , ' : ' + str(item.good_value) if item.good_value else ' : '],
            ['Stempel'         , ' : '],
        ]

        table = Table(data, colWidths=(20*mm, 30*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(0, 560, mm))

        c.setFont('Helvetica', 18)
        c.drawCentredString(180, 560, 'BDO')

        c.setFont('Helvetica-Bold', 5)
        c.drawCentredString(self.page_width/4, 545, 'Dokumen ini dicetak secara otomatis dengan "AREA 51 online system"')

        c.setFont('Helvetica-Bold', 4)
        c.drawCentredString(self.page_width/4, 538, 'untuk pengecekan status kiriman silakan mengunjungi www.area51logistik.com')

        c.setFont('Helvetica-Bold', 6)
        c.drawCentredString(360, 558, 'Petugas')
        c.drawCentredString(360, 545, '( ' + item.user.fullname.upper() + ' )')

	c.setFont('Helvetica-Bold', 6)
        c.drawCentredString(475, 583, 'Ttd. Penerima')
        c.drawCentredString(475, 545, '(                                )')


if __name__ == '__main__':
    r = Report()
    r.run()
