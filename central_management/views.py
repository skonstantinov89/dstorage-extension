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
    class Index(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            return render_to_response('main/central_main.html', context)
        # def post(self, request):
        #   context = RequestContext(request)
        #   return render_to_response('main/central_main.html', context)
    class preview(View):
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
            return render_to_response('preview_central/preview.html', locals(), context)
        
    class receipt(View):
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
                protocolID = int(protocolID)
                return render_to_response('receipt/list.html', locals(), context)
            
            else:
                protocolID = request.POST.get('protocolID', '')
                acceptedDocuments = request.POST.get('acceptedDocuments', '').split(',')
                rejectedDocuments = request.POST.get('rejectedDocuments', '').split(',')
                if len(acceptedDocuments) == 1 and acceptedDocuments[0] == '':
                    acceptedDocuments = []

                if len(rejectedDocuments) == 1 and rejectedDocuments[0] == '':
                    rejectedDocuments = []

                if acceptedDocuments:
                    requestList = []
                    for eachDocument in acceptedDocuments:
                        currentDocument = Document.objects.get(id=int(eachDocument))
                        currentDocument.status = 'in-warehouse'
                        currentDocument.location = 'storage 2'
                        currentDocument.centralManagementStartDate = datetime.datetime.now()
                        currentDocument.save()
                        requestList.append(Requests.objects.get(
                                                                    Q(documentID = currentDocument.id), 
                                                                    Q(protocolID = int(protocolID))
                                                                )
                                          )

                        for eachRequest in requestList:
                            eachRequest.status = 'verified'
                            eachRequest.verifierID = request.user
                            eachRequest.save()
                if rejectedDocuments:
                    requestList = []
                    for eachDocument in rejectedDocuments:
                        currentDocument = Document.objects.get(id=int(eachDocument))
                        requestList.append(Requests.objects.get(
                                                                    Q(documentID = currentDocument.id), 
                                                                    Q(protocolID = int(protocolID))
                                                                )
                                          )
                        for eachRequest in requestList:
                            eachRequest.status = 'not-verified'
                            eachRequest.verifierID = request.user
                            eachRequest.save()
                            
                return render_to_response('receipt/success.html', locals(), context)
            
            return render_to_response('receipt/error2.html', locals(), context)

    class search(View):
        
        def get(self,request):
            context = RequestContext(request)
            return render_to_response('search/search.html',context)
            
        def post(self, request):
            context = RequestContext(request)
            fields = {}
            for i in range(1,13):
                fields['field' + str(i)] = request.POST.get('field' + str(i), '')

            # documentData = list(Document.objects.filter(active=True).values_list('id', flat=True))
            # criteriaData = 
            searchButton = request.POST.get('searchButton', '')
            if searchButton != '':
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
                                                                        Q(field10__icontains = fields['field10']),
                                                                        Q(field11__icontains = fields['field11']),
                                                                        Q(field12__icontains = fields['field12']),
                                                                        # Q(documentID__status='in-warehouse')
                                                                    )

                return render_to_response('search/list.html', locals(), context)        
        
            return render_to_response('search/error.html', locals(), context)        
        
    class moveToArchive(View):
        class RequestTemplate(SimpleDocTemplate):
            def addPageTemplates(self,pageTemplates):
                """
                fix up the one and only Frame
                """
                if pageTemplates:
                    f = pageTemplates[0].frames[0]
                    f._leftPadding=f._rightPadding=f._topPadding=f._bottomPadding=0
                    f._geom()
                SimpleDocTemplate.addPageTemplates(self,pageTemplates)      

        def get(self,request):
            context = RequestContext(request)
            return render_to_response('move/search.html',context)

        def post(self, request):
            context = RequestContext(request)
            fields = {}
            for i in range(1,13):
                fields['field' + str(i)] = request.POST.get('field' + str(i), '')

            # documentData = list(Document.objects.filter(active=True).values_list('id', flat=True))
            # criteriaData = 
            searchButton = request.POST.get('searchButton', '')
            protocolButton = request.POST.get('protocolButton', '')
            listButton = request.POST.get('listButton', '')
            if searchButton != '':
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
                                                                        Q(field10__icontains = fields['field10']),
                                                                        Q(field11__icontains = fields['field11']),
                                                                        Q(field12__icontains = fields['field12']),
                                                                        Q(documentID__location='storage 2')
#                                                                         Q(documentID__status='in-warehouse')
                                                                    )
                print(len(criteriaData))
                return render_to_response('move_archive/list.html', locals(), context)
            elif protocolButton != '':
                archiveDocuments = request.POST.get('archiveDocuments', '').split(',')

                requestList = []

                if archiveDocuments:
                    newProtocol = Protocols.objects.create(
                                                userID = request.user,
                                                requestDate = datetime.datetime.now(),
                                                fromLocation = 'storage 2', # central
                                                toLocation = 'storage 3', # archive
                                            )
                    for eachDocument in archiveDocuments:
                        requestList.append(Requests(
                                                        documentID = Document.objects.get(id=int(eachDocument)),
                                                        status = 'in-progress',
                                                        protocolID = newProtocol
                                                   )
                                            )
                        currentDocument = Document.objects.get(id=int(eachDocument))
                        if currentDocument.status == 'in-courier' and currentDocument.location == 'storage 2':
                            requestList.pop()
                            newProtocol.delete()
                            return render_to_response('move/error_incorrect_documents.html', context)
                        else:
                            currentDocument.status = 'in-courier'
                            currentDocument.save()
                    if requestList:
                        Requests.objects.bulk_create(requestList)

                        response = HttpResponse(content_type='application/pdf')
                        response['Content-Disposition'] = 'attachment; filename="Protocol-' + str(datetime.datetime.now()) +'.pdf"'
                        signBoxCols = [6*cm,3*cm,6*cm]
                        signBoxStyle = [
                                        ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
                                        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                                        ('FONT',          (0,0), (-1,-1),  'n', 10)
                                        ]

                        header = Paragraph(u''' <strong> ПРИЕМО-ПРЕДАВАТЕЛЕН ПРОТОКОЛ <br/>
                        за предадено за съхранение досие/документ №(%s) </strong>'''%(str(newProtocol.id).zfill(5)),styleBoldCenter)
                        textBeforeTable = Paragraph(u'''Днес ……………….. г. подписаните ………………………………………. 
                        на длъжност …………………………………… и …………………………………. на длъжност  от ...........................................(поделение) 
                        предадохме   на ……………………… на  длъжност ...................................................................................... 
                        към Управление „Логистика“ в ЦУ    …............../............................................/ броя досиета с прилежащите им описи,
                        оформени в ……..броя пликове/кутии. <br/>
                        <br/> <b> Декларираме </b> с подписите си, че целостта на пликовете/кутиите не е нарушена и са запечатани,
                        съгласно изискванията Процедура за контрол, предаване и централизирано съхранение на оригинални
                        документи по кредитни сделки на бизнес клиенти.
                        ''',styleNormal)


                        textUnderTable = Paragraph(u'''Настоящия протокол се подписва в два еднакви екземпляра, по един за всяка от страните.<br/><br/>
                            ''', styleNormal)
                        signBox = [

                            [u'Дата: ' + datetime.datetime.now().strftime("%d.%m.%Y")+u'г.', u'', u''],
                            [u'', u''],

                            [u'ПРИЕЛ: ....................................',  u'',  u'ПРЕДАЛ: .....................................'],

                            [u'Име:  .........................................',  u'',  u'Име: ..............................................'],
                        ]
                        footerText = Paragraph('''
                            Констатирани несъответствия от приемащата комисия:
                            ……………………………………………………………………………………………………………………………………
                            ……………………………………………………………………………………………………………………………………
                            ………………………………………………………………………………………………………………………………….

                            <br/><br/>Срок за отстраняване на несъответствия:…............................

                            <br/><br/>За ДКАКСБК (Име, длъжност и подпис)
                            <br/><br/>……………………………
                            
                            <br/><br/>За Централен архив (Име и подпис)
                            <br/><br/>……………………………
                            ''', styleNormal)
                        cfs=[Spacer(0, 0.3*cm),
                            header,
                            Spacer(0, 0.7*cm),
                            textBeforeTable,
                            Spacer(0, 0.3*cm),
                            textUnderTable,
                            Spacer(0, 0.3*cm),
                            Table(signBox, style=signBoxStyle, colWidths=signBoxCols),
                            Spacer(0, 0.5*cm),
                            footerText
                            ]
                        self.RequestTemplate(response, bottomMargin=1.3*cm, topMargin=1.3*cm).build(cfs)
                        return response
            
            elif listButton != '':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="Document-list-' + str(datetime.datetime.now()) +'.csv"'
                archiveDocuments = request.POST.get('archiveDocuments', '').split(',')

                if archiveDocuments:
                    # with codecs.open('Document-list-' + str(datetime.datetime.now()), 'w', 'utf-8') as listFile:
                    writer = csv.writer(response,delimiter='|')

                    writer.writerow(['Име на регион','Име на клон','Клиентски номер','ЕИК/БУЛСТАТ','Име на клиент','Дата на договор','Номер на сметка','Размер на кредит','Размер на кредит','Валута','КИ идентификатор','Вид на документ','Описание'])
                    for eachDocument in archiveDocuments:
                        criterionObject = Criterion.objects.get(documentID = int(eachDocument))
                        writer.writerow([
                                            criterionObject.field1,
                                            criterionObject.field2,
                                            criterionObject.field3,
                                            criterionObject.field4,
                                            criterionObject.field5,
                                            criterionObject.field6,
                                            criterionObject.field7, 
                                            criterionObject.field8, 
                                            criterionObject.field9, 
                                            criterionObject.field10, 
                                            criterionObject.field11, 
                                            criterionObject.field12
                                        ])
                        currentDocument = Document.objects.get(id = int(eachDocument))
                        currentDocument.status = 'in-courier'
                        currentDocument.save()    
                    
                    return response
            return render_to_response('move/error.html', locals(), context)
        
    class conformation(View):
        @method_decorator(login_required)
        
        def get(self,request):
            context = RequestContext(request)
            return render_to_response('conformation/search.html',context)
        
        def post(self, request):
            context = RequestContext(request)
            
            protocolID = request.POST.get('protocolID', '')

            confirmButton = request.POST.get('confirmButton', '')
            rejectButton = request.POST.get('rejectButton', '')

            if protocolID == '':
                return render_to_response('conformation/error.html', locals(), context)
                 
            if confirmButton != '':
                requestData=Requests.objects.select_related().filter(protocolID = int(protocolID))
            
                frontData = []
                for eachRequest in requestData:
                    
                    currentDocument = Document.objects.get(id=eachRequest.documentID.id)
                    currentDocument.status = 'in-warehouse'
                    currentDocument.location = 'storage 3'
                    currentDocument.archiveStartDate = datetime.datetime.now()
                    currentDocument.save()                       
                    
                    eachRequest.status = 'verified'
                    eachRequest.verifierID = request.user
                    eachRequest.save()
                    protocolID = int(protocolID)
                return render_to_response('conformation/success.html', locals(), context)
            
            elif rejectButton != '':
                requestData=Requests.objects.select_related().filter(protocolID = int(protocolID))
            
                frontData = []
                for eachRequest in requestData:
                    
                    currentDocument = Document.objects.get(id=eachRequest.documentID.id)
                    currentDocument.status = 'in-warehouse'
                    currentDocument.location = 'storage 2'
                    currentDocument.save()                       
                    
                    eachRequest.status = 'not-verified'
                    eachRequest.verifierID = request.user
                    eachRequest.save()
                    protocolID = int(protocolID)
                
                return render_to_response('conformation/rejection.html', locals(), context)            
            
            