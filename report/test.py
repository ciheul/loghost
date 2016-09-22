from datetime import datetime
import os

from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.units import cm, mm, inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle


class Report:
    def __init__(self):
        self.page_width, self.page_height = A4
        self.n_style = ParagraphStyle(name='normal',
                                      spaceAfter=50,
                                      fontSize=6,
                                      fontName='Helvetica')

    def run(self):
        c = canvas.Canvas('hello.pdf', pagesize=A4)
        self.generate(c)
        c.showPage()
        c.save()

    def coord(self, x, y, unit=1):
        # x, y = x*unit, self.page_height - y*unit
        return x, y

    def generate(self, c):
        c.translate(cm, cm)

        # logo
        logo_path = 'images/area-51-logistik.png'
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
        c.drawCentredString(self.page_width/2, 780,
                            "e-CONSIGNMENT NOTE (e-connote)")

        # time
        c.setFont('Helvetica', 6)
        now = datetime.now()
        c.drawCentredString(self.page_width/2, 768,
                            now.strftime('%Y/%m/%d %H:%M:%S'))

        c.setFont('Helvetica', 12)
        c.drawCentredString(self.page_width/2, 751, 'REG15')

        # a list of items and their metrics
        data = [
            ['Keterangan', 'Jml', 'Berat', '' , 'Dimensi', '' , 'Berat' ],
            [''          , ''   , 'Asli' , 'L', 'H'      , 'W', 'Volume'],
            ['ND'        , '1'  , '1.00' , '' , ''       , '' , '0.00'  ],
        ]
        col_widths = (20*mm, 10*mm, 10*mm, 10*mm, 10*mm, 10*mm, 10*mm)
        table = Table(data, colWidths=col_widths)

        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            # align for header
            ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
            # align for body 
            ('ALIGN', (0, 2), (-1, -1), 'RIGHT'),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(330, 740, mm))

        # sender and receiver
        data = [
            ['Kota Asal'    , ': CGK10000', 'Kota Tujuan', ': BDO1000'],
            ['No. Pelanggan', ': 10533306', 'Pembayaran' , ': Cash'],
        ]

        table = Table(data, colWidths=(20*mm, 38*mm, 15*mm, 20*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(0, 715, mm))

        c.setFont('Helvetica', 6)
        sender_info = "<b>Pengirim</b> : PT. NUSA CIPTA SOLUSI"
        sender = Paragraph(sender_info, self.n_style)
        sender.wrapOn(c, self.page_width, self.page_height)
        sender.drawOn(c, *self.coord(0, 695, mm))

        c.drawString(0, 692, "JL. PINTU AIR 5 NO. 38, LT 2")
        c.drawString(0, 682, "(DI ATAS BRILLIANT TOUR)")
        c.drawString(0, 672, "JAKARTA PUSAT")

        receiver_info = "<b>Penerima</b> : PT. LOGHOST INDONESIA"
        receiver = Paragraph(receiver_info, self.n_style)
        receiver.wrapOn(c, self.page_width, self.page_height)
        receiver.drawOn(c, *self.coord(0, 647, mm))
        c.drawString(0, 643, "JL. BATUNUNGGAL JELITA II NO. 22")
        c.drawString(0, 633, "PERUMAHAN BATUNUNGGAL INDAH")
        c.drawString(0, 623, "BANDUNG")

        data = [
            ['Attn'    , ' :'            ],
            ['Telepon' , ' : +6221345912'],
            ['Kode Pos', ' : 10710'      ],
            ['Ref No'  , ' :'            ],
            [''        , ''              ],
            ['Attn'    , ' :'            ],
            ['Telepon' , ' : +6221345912'],
            ['Kode Pos', ' : 10710'      ],
        ]

        table = Table(data, colWidths=(10*mm, 30*mm))
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), -2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(c, self.page_width, self.page_height)
        table.drawOn(c, *self.coord(200, 615, mm))

        data = [
            ['Instruksi Khusus', ' :'          ],
            ['Keterangan'      , ' : SPAREPART'],
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
        table.drawOn(c, *self.coord(0, 560, mm))

        c.setFont('Helvetica', 18)
        c.drawCentredString(self.page_width/2, 550, 'BDO')

        c.setFont('Helvetica-Bold', 5)
        c.drawCentredString(210, 535, 'Dokumen ini dicetak secara otomatis dengan "AREA 51 online system"')

        c.setFont('Helvetica-Bold', 4)
        c.drawCentredString(210, 528, 'untuk pengecekan status kiriman silakan mengunjungi www.area51logistik.com')

        c.setFont('Helvetica-Bold', 5)
        c.drawCentredString(440, 535, 'Dengan menandatangani e-connote ini pengirim telah membaca, memahami dan sepakat untuk')
        c.drawCentredString(440, 528, 'terikat dengan Syarat Standar Pengiriman (SSP). PT. Area 51 Logistik yang tercantum dalam') 
        c.drawCentredString(440, 521, 'halaman 2 (dua) yang merupakan satu kesatuan tidak terpisahkan dari e-connote ini.')

if __name__ == '__main__':
    r = Report()
    r.run()
