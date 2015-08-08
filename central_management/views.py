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

class Central(View):   
    print('11')      
    class Index(View):
        print('22')
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            return render_to_response('main/central_main.html', context)
        # def post(self, request):
        #   context = RequestContext(request)
        #   return render_to_response('main/central_main.html', context)
    class preview(View):
        print('33')
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            frontData = []
            documentData = Document.objects.filter(active=True)
            for eachDocument in documentData:
                frontData.append({
                    'document': eachDocument,
                    'fields': Criterion.objects.get(documentID = eachDocument.id),
                    })
            return render_to_response('preview/preview.html', locals(), context)
        
    class receipt(View):
        print('44')
        @method_decorator(login_required)
        
        def get(self,request):
            context = RequestContext(request)
            return render_to_response('receipt/search.html',context)
        
        def post(self, request):
            context = RequestContext(request)
            
            protocolID = request.POST.get('protocolID', '')
        
            searchButton = request.POST.get('searchButton', '')

            if protocolID == '':
                return render_to_response('receipt/error1.html', locals(), context)
                
            if searchButton != '':
                requestData=Requests.objects.select_related().filter(protocolID = int(protocolID))
            
                frontData = []
                for eachRequest in requestData:
                    frontData.append({
                        'request': eachRequest,
                        'fields': Criterion.objects.get(documentID = eachRequest.documentID.id),
                        })
                return render_to_response('receipt/list.html', locals(), context)
            
            else:
                acceptedDocuments = request.POST.get('acceptedDocuments', '').split(',')
                rejectedDocuments = request.POST.get('rejectedDocuments', '').split(',')

                if acceptedDocuments or rejectedDocuments:
                    
                    requestList = []
                    for eachDocument in acceptedDocuments:
                        currentDocument = Document.objects.get(id=int(eachDocument))
                        currentDocument.status = 'in-warehouse'
                        currentDocument.location = 'storage 2'
                        currentDocument.centralManagementStartDate = datetime.datetime.now()
                        currentDocument.save()                       
                        requestList.append(Requests.objects.get(documentID = currentDocument.id))
                        for eachRequest in requestList:
                            eachRequest.status = 'verified'
                            eachRequest.verifierID = request.userr
                            eachRequest.save()
                    requestList = []
                    for eachDocument in rejectedDocuments:
                        currentDocument = Document.objects.get(id=int(eachDocument))
                        requestList.append(Requests.objects.get(documentID = currentDocument.id))                   
                        for eachRequest in requestList:
                            eachRequest.status = 'not-verified'
                            eachRequest.verifierID = request.user
                            eachRequest.save()
                            
                    return render_to_response('receipt/success.html', locals(), context)
            
            return render_to_response('receipt/error2.html', locals(), context)

    class search(View):
        
        print('1')
        def get(self,request):
            context = RequestContext(request)
            print('2')
            return render_to_response('search/search.html',context)
            
        def post(self, request):
            print('3')
            context = RequestContext(request)
            fields = {}
            for i in range(1,10):
                fields['field' + str(i)] = request.POST.get('field' + str(i), '')

            # documentData = list(Document.objects.filter(active=True).values_list('id', flat=True))
            # criteriaData = 
            searchButton = request.POST.get('searchButton', '')
            if searchButton != '':
                print('4')
                criteriaData=Criterion.objects.select_related().filter(
                                                                        Q(field1__icontains = fields['field1']),
                                                                        Q(field2__icontains = fields['field2']),
                                                                        Q(field3__icontains = fields['field3']),
                                                                        Q(field4__icontains = fields['field4']),
                                                                        Q(field5__icontains = fields['field5']),
                                                                        Q(field6__icontains = fields['field6']),
                                                                        Q(field7__icontains = fields['field7']),
                                                                        Q(field8__icontains = fields['field8']),
                                                                        Q(field9__icontains = fields['field9']),
                                                                        Q(documentID__status='in-warehouse')
                                                                    )

                print('5')
                return render_to_response('search/list.html', locals(), context)        
        
            return render_to_response('search/error.html', locals(), context)        
        
        