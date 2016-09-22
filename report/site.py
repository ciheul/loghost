import copy
from datetime import datetime, timedelta, time as tiime
import os
from StringIO import StringIO

from django.http import HttpResponse
from django.conf import settings

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


class SiteReport: 
    def print_blank(self, request):

        # setting for sending back the PDF in response
        filename = 'blank.pdf'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="%s"' % filename

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
        c.drawString(30, 430, "Kota Asal : ")
        c.drawString(250, 430, "Kota Tujuan : ")
        c.drawString(30, 415, "Pembayaran : ")

        ##### SENDER #####
        c.drawString(30, 380, "Pengirim : ")
        
        c.drawString(30, 335, "Kode Pos : ")

        sender_phone = ''
        c.drawString(30, 320, "Telepon : " + sender_phone)

        ##### RECEIVER #####
        c.drawString(30, 280, "Penerima: ")

        receiver_zip_code = ''
        c.drawString(30, 235, "Kode Pos : " + receiver_zip_code)

        receiver_phone = ''
        c.drawString(30, 220, "Telepon : " + receiver_phone)

        ##### ADDITIONAL INFORMATIO #####
        good_name = ''
        c.drawString(350, 380, "Nama Barang: " + good_name)

        good_value = ''
        c.drawString(350, 365, "Nilai Barang: " + good_value)

        instruction = ''
        c.drawString(350, 350, "Instruksi: " + instruction)

        information = ''
        c.drawString(350, 335, "Information: " + information)

        c.drawString(350, 280, "Berat ")
        c.drawString(350, 265, "Panjang ")
        c.drawString(350, 250, "Lebar ")
        c.drawString(350, 235, "Tinggi ")
        c.drawString(350, 220, "Jumlah ")
        
        c.drawString(600, 380, "No. AWB : ")
        c.drawString(600, 365, "Layanan : ")
        c.drawString(600, 350, "Jenis Kiriman : ")
        c.drawString(600, 280, "Biaya Kirim : (IDR) ")
        c.drawString(600, 265, "Biaya Lain-lain : (IDR) ") 
        c.drawString(600, 250, "Total Biaya : (IDR) ") 

        c.drawString(650, 170, "Diterima") 

        c.drawString(80, 110, "Dokumen ini dicetak menggunakan sistem online Area 51 secara otomatis") 
        c.drawString(50, 95, "untuk mengetahui status paket Anda, mohon mengunjungi web www.area51logistik.com.") 

        c.showPage()
        c.save()

        return response
