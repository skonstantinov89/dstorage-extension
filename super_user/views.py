from django.shortcuts import render

# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.views.generic import View

from django.template import RequestContext
# from system.forms import LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

from system.models import Document, Requests, Criterion, Files, Protocols
from office.forms import DocumentForm
import datetime, codecs, csv
# reportlab imports

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import Paragraph
from reportlab.platypus import Frame, Spacer, Image, Table
from reportlab.platypus.flowables import KeepInFrame
from reportlab.platypus.flowables import PageBreak
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate
# from lxml.html.builder import BIG
pdfmetrics.registerFont(TTFont('n',       'FreeSans.ttf'))
pdfmetrics.registerFont(TTFont('i',       'FreeSansOblique.ttf'))
pdfmetrics.registerFont(TTFont('b',       'FreeSansBold.ttf'))
pdfmetrics.registerFont(TTFont('bi',      'FreeSansBoldOblique.ttf'))
# pdfmetrics.registerFont(TTFont('bullet',  'opens___.ttf'))
pdfmetrics.registerFont(TTFont('barcode', 'code128.TTF'))
addMapping('n', 0, 0, 'n')
addMapping('n', 0, 1, 'i')
addMapping('n', 1, 0, 'b')
addMapping('n', 1, 1, 'bi')
styleNormal = ParagraphStyle(name = 'normal', alignment=TA_JUSTIFY, fontName='n', fontSize = 10, \
                             leading = 14)
styleCenter = ParagraphStyle(name = 'normal', alignment=TA_CENTER, fontName='n', fontSize = 10, \
                             leading = 14)
styleBold = ParagraphStyle(name = 'normal', alignment=TA_LEFT, fontName='b', fontSize = 12, \
                             leading = 14)
styleBoldCenter = ParagraphStyle(name = 'normal', alignment=TA_CENTER, fontName='b', fontSize = 12, \
                             leading = 12*1.2)
styleRight = ParagraphStyle(name = 'normal', alignment=TA_RIGHT, fontName='n', fontSize = 12, \
                             leading = 14)
styleNormalFLIspace = ParagraphStyle(name = 'normal', alignment=TA_JUSTIFY, fontName='n', fontSize = 12, \
                             leading = 14, firstLineIndent=0.5*cm, spaceBefore = 0.7*cm, spaceAfter = 1*cm)
styleDA = ParagraphStyle(name = 'normal', alignment=TA_LEFT, fontName='b', fontSize = 12, \
                             leading = 14)
styleDAcenter = ParagraphStyle(name = 'normal', alignment=TA_CENTER, fontName='b', fontSize = 12, \
                             leading = 14)
styleDAbarcode = ParagraphStyle(name = 'normal', alignment=TA_CENTER, fontName='barcode', fontSize = 30, \
                             leading = 28)
styleBullet = ParagraphStyle(name = 'normal', alignment=TA_JUSTIFY, fontName='n', fontSize = 30, \
                             leading = 28, bulletFontName = 'bullet', bulletFontSize = 12, \
                             bulletIndent = 2*cm, leftIndent = 2.5*cm, spaceAfter = 8)
styleStrangeBullet = ParagraphStyle(name = 'normal', alignment=TA_JUSTIFY, fontName='n', fontSize = 30, \
                             leading = 28, bulletFontName = 'n', bulletFontSize = 12, \
                             bulletIndent = 2*cm, leftIndent = 2.5*cm, spaceAfter = 8)

# reportlab frame measurements - left margin, bottom margin, width, [first page height, other pages height]
mflm, mfbm, mfw, mfh = 1, 0.7, 19, [28, 28]


#end reportlab imports


class SuperUser(View):     
    class index(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            return render_to_response('main/super_user_main.html', locals(), context)