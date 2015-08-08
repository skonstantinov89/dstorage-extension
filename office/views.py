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


class Office(View):
    class finishRequests(View):
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


        @method_decorator(login_required)
        def get(self,request):
            context = RequestContext(request)
            return render_to_response('request/search.html',context)
        
        def post(self, request):
            context = RequestContext(request)
            protocolID = request.POST.get('protocolID', '')
            searchButton = request.POST.get('searchButton', '')
            confirmButton = request.POST.get('confirmButton', '')

            if searchButton != '':
                if protocolID != '':
                    try:
                        requestData = Requests.objects.select_related().filter(
                                                                                    Q(protocolID = int(protocolID)),
                                                                                    Q(status='not-verified')
                                                                                  )
                    except:
                        return render_to_response('request/error_mising_protocol.html', context)
                    frontData = []

                    for eachRequest in requestData:
                        frontData.append({
                            'request': eachRequest,
                            'document': Criterion.objects.select_related().get(documentID = eachRequest.documentID)
                            })
                    searchButton = ''
                    return render_to_response('request/list.html', locals(), context)
                else:
                    return render_to_response('request/error_mising_protocol.html', context)
            
            elif confirmButton != '':
                incorrectRequests = request.POST.get('incorrectRequests', '').split(',')
                missingRequests = request.POST.get('missingRequest', '').split(',')
                if len(incorrectRequests)!=0 and incorrectRequests[0]!='':
                    
                    for eachRequest in incorrectRequests:
                        currentRequest = Requests.objects.select_related().get(id=int(eachRequest))
                        currentRequest.status = 'incorrect'
                        currentRequest.save()
                        currentDocument = Document.objects.get(id=currentRequest.documentID.id)
                        currentDocument.location = 'storage 1'
                        currentDocument.status = 'in-warehouse'
                        currentDocument.centralManagementStartDate = None
                        currentDocument.save()
                    
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="Protocol-for-incorrects-' + str(datetime.datetime.now()) +'.pdf"'
                    boxstyle = [
                                    ('ALIGN',         (0,0), (-1,0), 'CENTER'),
                                    ('ALIGN',         (0,1), (-1,-1), 'CENTER'),
                                    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                                    ('TOPPADDING',    (0,0), (-1,-1), 1),
                                    ('LEFTPADDING',   (0,0), (-1,-1), 10),
                                    ('GRID',          (0,0), (-1,-1), 0.3, colors.black),
                                    ('FONT',          (0,0), (-1,0),  'b', 10),
                                    ('FONT',          (0,1), (-1,-1),  'n', 10),
                                ]
                    boxText =   [
                            [u'Документ (критерии)', u'Забележка']
                        ]

                    boxCols = [12*cm, 5*cm]
                    signBoxCols = [6*cm,3*cm,6*cm]
                    signBoxStyle = [
                                    ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
                                    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                                    ('FONT',          (0,0), (-1,-1),  'n', 10)
                                    ]

                    criteriaFront = ''
                    for eachRequest in incorrectRequests:
                        requestObject = Requests.objects.select_related().get(id=int(eachRequest))
                        criterionObject = Criterion.objects.get(documentID = requestObject.documentID)
                        criteriaFront += 'Име на регион: ' + criterionObject.field1 + '<br/>'
                        criteriaFront += 'Име на клон: ' + criterionObject.field2 + '<br/>'
                        criteriaFront += 'Клиентски номер: ' + criterionObject.field3 + '<br/>'
                        criteriaFront += 'ЕИК/БУЛСТАТ: ' + criterionObject.field4 + '<br/>'
                        criteriaFront += 'Име на клиент: ' + criterionObject.field5 + '<br/>'
                        criteriaFront += 'Дата на договор: ' + criterionObject.field6 + '<br/>'
                        criteriaFront += 'Номер на сметка: ' + criterionObject.field7 + '<br/>'
                        criteriaFront += 'Размер на кредит: ' + criterionObject.field8 + '<br/>'
                        criteriaFront += 'Валута: ' + criterionObject.field9 + '<br/>'
                        criteriaFront += 'КИ идентификатор: ' + criterionObject.field10 + '<br/>'
                        criteriaFront += 'Вид на документ: ' + criterionObject.field11 + '<br/>'
                        criteriaFront += 'Описание: ' + criterionObject.field12 + '<br/>'

                    header = Paragraph(u''' <strong> ПРИЛОЖЕНИЕ КЪМ ПРОТОКОЛ: (%s) </strong>'''%(str(requestObject.protocolID.id).zfill(5)),styleBoldCenter)
                    textBeforeTable = Paragraph(u'''Долуописаните документи бяха предадени на представител на ДСК със забележка: 
                        <b> ГРЕШНО ИЗПРАТЕНИ </b>
                        ''',styleNormal)
                    boxText.append([
                        Paragraph(criteriaFront,styleCenter),
                        Paragraph('Некоректно изпратена друга и върната', styleCenter)
                        ])
                    textUnderTable = Paragraph(u'''Настоящия протокол се подписва в два еднакви екземпляра,
                     по един за всяка от страните и се прикрепя към единия протокол и се изпраща обратно за другия.<br/><br/>
                        ''', styleNormal)
                    signBox = [

                        [u'Дата: ' + datetime.datetime.now().strftime("%d.%m.%Y")+u'г.', u'', u''],
                        [u'', u''],

                        [u'ПРИЕЛ: ....................................',  u'',  u'ПРЕДАЛ: .....................................'],

                        [u'Име:  .........................................',  u'',  u'Име: ..............................................'],

                    ]
                    cfs=[Spacer(0, 0.3*cm),
                        header,
                        Spacer(0, 0.3*cm),
                        textBeforeTable,
                        Spacer(0, 0.3*cm),
                        Table(boxText, style=boxstyle, colWidths=boxCols),
                        Spacer(0, 0.3*cm),
                        textUnderTable,
                        Spacer(0, 0.3*cm),
                        Table(signBox, style=signBoxStyle, colWidths=signBoxCols),
                        Spacer(0, 0.5*cm),
                        Paragraph(u'________________________________________________________________________________' , styleNormal),
                        Spacer(0, 0.3*cm),
                        header,
                        Spacer(0, 0.3*cm),
                        textBeforeTable,
                        Spacer(0, 0.3*cm),
                        Table(boxText, style=boxstyle, colWidths=boxCols),
                        Spacer(0, 0.3*cm),
                        textUnderTable,
                        Spacer(0, 0.3*cm),
                        Table(signBox, style=signBoxStyle, colWidths=signBoxCols),
                        Spacer(0, 0.3*cm),
                         ]
                    self.RequestTemplate(response, bottomMargin=1.3*cm, topMargin=1.3*cm).build(cfs)
                    return response

                if len(missingRequests)!=0 and missingRequests[0]!='':
                    for eachRequest in missingRequests:

                        currentRequest = Requests.objects.select_related().get(id=int(eachRequest))
                        currentRequest.status = 'missing'
                        currentRequest.save()
                        currentDocument = Document.objects.get(id=currentRequest.documentID.id)
                        currentDocument.location = 'storage 1'
                        currentDocument.status = 'in-warehouse'
                        currentDocument.centralManagementStartDate = None
                        currentDocument.save()
                    
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="Protocol-for-incorrects-' + str(datetime.datetime.now()) +'.pdf"'
                    boxstyle = [
                                    ('ALIGN',         (0,0), (-1,0), 'CENTER'),
                                    ('ALIGN',         (0,1), (-1,-1), 'CENTER'),
                                    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                                    ('TOPPADDING',    (0,0), (-1,-1), 1),
                                    ('LEFTPADDING',   (0,0), (-1,-1), 10),
                                    ('GRID',          (0,0), (-1,-1), 0.3, colors.black),
                                    ('FONT',          (0,0), (-1,0),  'b', 10),
                                    ('FONT',          (0,1), (-1,-1),  'n', 10),
                                ]
                    boxText =   [
                            [u'Документ (критерии)', u'Забележка']
                        ]

                    boxCols = [12*cm, 5*cm]
                    signBoxCols = [6*cm,3*cm,6*cm]
                    signBoxStyle = [
                                    ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
                                    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                                    ('FONT',          (0,0), (-1,-1),  'n', 10)
                                    ]

                    criteriaFront = ''
                    for eachRequest in missingRequests:
                        requestObject = Requests.objects.select_related().get(id=int(eachRequest))
                        criterionObject = Criterion.objects.get(documentID = requestObject.documentID)                        
                        criteriaFront += 'Име на регион: ' + criterionObject.field1 + '<br/>'
                        criteriaFront += 'Име на клон: ' + criterionObject.field2 + '<br/>'
                        criteriaFront += 'Клиентски номер: ' + criterionObject.field3 + '<br/>'
                        criteriaFront += 'ЕИК/БУЛСТАТ: ' + criterionObject.field4 + '<br/>'
                        criteriaFront += 'Име на клиент: ' + criterionObject.field5 + '<br/>'
                        criteriaFront += 'Дата на договор: ' + criterionObject.field6 + '<br/>'
                        criteriaFront += 'Номер на сметка: ' + criterionObject.field7 + '<br/>'
                        criteriaFront += 'Размер на кредит: ' + criterionObject.field8 + '<br/>'
                        criteriaFront += 'Валута: ' + criterionObject.field9 + '<br/>'
                        criteriaFront += 'КИ идентификатор: ' + criterionObject.field10 + '<br/>'
                        criteriaFront += 'Вид на документ: ' + criterionObject.field11 + '<br/>'
                        criteriaFront += 'Описание: ' + criterionObject.field12 + '<br/>'

                    header = Paragraph(u''' <strong> ПРИЛОЖЕНИЕ КЪМ ПРОТОКОЛ: (%s) </strong>'''%(str(requestObject.protocolID.id).zfill(5)),styleBoldCenter)
                    textBeforeTable = Paragraph(u'''Долуописаните документи бяха предадени на представител на ДСК със забележка: 
                        <b> ЛИПСВАЩИ </b>
                        ''',styleNormal)
                    boxText.append([
                        Paragraph(criteriaFront,styleCenter),
                        'Липсващ'
                        ])
                    textUnderTable = Paragraph(u'''Настоящия протокол се подписва в два еднакви екземпляра,
                     по един за всяка от страните и се прикрепя към единия протокол и се изпраща обратно за другия.<br/><br/>
                        ''', styleNormal)
                    signBox = [
                        [u'Дата: ' + datetime.datetime.now().strftime("%d.%m.%Y")+u'г.', u'', u''],
                        [u'', u''],

                        [u'ПРИЕЛ: ....................................',  u'',  u'ПРЕДАЛ: .....................................'],

                        [u'Име:  .........................................',  u'',  u'Име: ..............................................'],

                    ]
                    cfs=[Spacer(0, 0.3*cm),
                        header,
                        Spacer(0, 0.3*cm),
                        textBeforeTable,
                        Spacer(0, 0.3*cm),
                        Table(boxText, style=boxstyle, colWidths=boxCols),
                        Spacer(0, 0.3*cm),
                        textUnderTable,
                        Spacer(0, 0.3*cm),
                        Table(signBox, style=signBoxStyle, colWidths=signBoxCols),
                        Spacer(0, 0.5*cm),
                        Paragraph(u'________________________________________________________________________________' , styleNormal),
                        Spacer(0, 0.3*cm),
                        header,
                        Spacer(0, 0.3*cm),
                        textBeforeTable,
                        Spacer(0, 0.3*cm),
                        Table(boxText, style=boxstyle, colWidths=boxCols),
                        Spacer(0, 0.3*cm),
                        textUnderTable,
                        Spacer(0, 0.3*cm),
                        Table(signBox, style=signBoxStyle, colWidths=signBoxCols),
                        Spacer(0, 0.3*cm),
                         ]
                    self.RequestTemplate(response, bottomMargin=1.3*cm, topMargin=1.3*cm).build(cfs)
                    return response

    class moveToCentral(View):
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
            for i in range(1,10):
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
                                                                        Q(documentID__status='in-warehouse')
                                                                    )

                return render_to_response('move/list.html', locals(), context)
            elif protocolButton != '':
                centralDocuments = request.POST.get('centralDocuments', '').split(',')
                archiveDocuments = request.POST.get('archiveDocuments', '').split(',')

                requestList = []
                if centralDocuments:
                    newProtocol = Protocols.objects.create(
                                                userID = request.user,
                                                requestDate = datetime.datetime.now(),
                                                fromLocation = 'storage 1', # office
                                                toLocation = 'storage 2', # central
                                            )
                    for eachDocument in centralDocuments:
                        if eachDocument not in archiveDocuments:
                            requestList.append(Requests(
                                                            documentID = Document.objects.get(id=int(eachDocument)),
                                                            status = 'in-progress',
                                                            protocolID = newProtocol
                                                       )
                                                )
                            currentDocument = Document.objects.get(id=int(eachDocument))
                            if currentDocument.status == 'in-courier' and currentDocument.location == 'storage 1':
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

                elif archiveDocuments:
                    newProtocol = Protocols.objects.create(
                                                userID = request.user,
                                                requestDate = datetime.datetime.now(),
                                                fromLocation = 'storage 1', # office
                                                toLocation = 'storage 2', # central
                                            )
                    for eachDocument in centralDocuments:
                        if eachDocument in archiveDocuments:
                            requestList.append(Requests(
                                                            documentID = Document.objects.get(id=int(eachDocument)),
                                                            status = 'in-progress',
                                                            protocolID = newProtocol
                                                       )
                                                )
                            currentDocument = Document.objects.get(id=int(eachDocument))
                            if currentDocument.status == 'in-courier' and currentDocument.location == 'storage 1':
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
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="Document-list-' + str(datetime.datetime.now()) +'.pdf"'
                centralDocuments = request.POST.get('centralDocuments', '').split(',')
                archiveDocuments = request.POST.get('archiveDocuments', '').split(',')

                text = Paragraph(u'ОПИС',styleBoldCenter)
                if centralDocuments:
                    boxTextCentral = []
                    boxstyle = [
                                    ('ALIGN',         (0,0), (-1,0), 'CENTER'),
                                    ('ALIGN',         (0,1), (-1,-1), 'CENTER'),
                                    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                                    ('TOPPADDING',    (0,0), (-1,-1), 1),
                                    ('LEFTPADDING',   (0,0), (-1,-1), 10),
                                    ('GRID',          (0,0), (-1,-1), 0.3, colors.black),
                                    ('FONT',          (0,0), (-1,0),  'b', 10),
                                    ('FONT',          (0,1), (-1,-1),  'n', 10),
                                ]
                    boxTextCentral =   [
                            [u'Документ (критерии)', u'Забележка']
                        ]

                    boxCols = [12*cm, 5*cm]

                    for eachDocument in centralDocuments:
                        criterionObject = Criterion.objects.get(documentID = int(eachDocument))
                        boxTextCentral.append(
                                                [
                                                Paragraph(str(
                                                    '<b> Име на регион: </b> ' + criterionObject.field1 + '<br/>' + 
                                                    '<b> Име на клон: </b>' + criterionObject.field2 + '<br/>' + 
                                                    '<b> Клиентски номер: </b>' + criterionObject.field3 + '<br/>' + 
                                                    '<b> ЕИК/БУЛСТАТ: </b>' + criterionObject.field4 + '<br/>' + 
                                                    '<b> Име на клиент: </b> ' + criterionObject.field5 + '<br/>' + 
                                                    '<b> Дата на договор: </b>' + criterionObject.field6 + '<br/>' + 
                                                    '<b> Номер на сметка: </b>' + criterionObject.field7 + '<br/>' +
                                                    '<b> Размер на кредит: </b>' + criterionObject.field8 + '<br/>' +
                                                    '<b> Валута: </b>' + criterionObject.field9 + '<br/>' +
                                                    '<b> КИ идентификатор: </b>' + criterionObject.field10 + '<br/>' +
                                                    '<b> Вид на документ: </b> ' + criterionObject.field11 + '<br/>' +
                                                    '<b> Описание: </b>' + criterionObject.field12 + '<br/>')
                                                    , styleNormal),
                                                ''
                                                ]
                                            )
                    cfs_Central=[
                                    Spacer(0, 0.2*cm),
                                    text,
                                    Spacer(0, 0.5*cm),
                                    Table(boxTextCentral, style=boxstyle, colWidths=boxCols),
                                    Spacer(0, 1*cm),
                                    PageBreak()
                                ]
                    self.RequestTemplate(response, bottomMargin=1.3*cm, topMargin=1.3*cm).build(cfs_Central)
                    return response


            return render_to_response('move/error.html', locals(), context)

    class preview(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            frontData = []
            documentData = Document.objects.filter(active=True)
            for eachDocument in documentData:
                print (eachDocument.id)
                frontData.append({
                    'document': eachDocument,
                    'fields': Criterion.objects.get(documentID = eachDocument.id),
                    })
            return render_to_response('preview/preview.html', locals(), context)

    class createBulk(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            form = DocumentForm() # A empty, unbound form
            return render_to_response ('create/bulk.html',locals(), context)

        @method_decorator(login_required)
        def post(self, request):
            context = RequestContext(request)
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                recordsCount = request.POST.get('recordsCount', '')
                recordsCount = int(recordsCount)
                newdoc = Files(docfile = request.FILES['docfile'])
                newdoc.save()
                infilename = newdoc.docfile.url
                mainarray = []
                with codecs.open(infilename, 'r', 'utf-8') as csvfile:
                    csvReader = csv.reader(csvfile, delimiter='|')
                    next(csvReader)  # skip header
                    for record in csvReader:
                        mainarray.append(record)
                    for eachElement in mainarray:
                        if len(eachElement) != 12:
                            return render_to_response('create/file_struct_error.html', context)
                    else:
                        if len(mainarray) != recordsCount:
                            return render_to_response('create/incorrect_count.html', context)
                        else:
                            criterionsList = []
                            for fields in mainarray:
                                newDocument = Document.objects.create(
                                            active = True,
                                            status = 'in-warehouse',
                                            location = 'storage 1',
                                            officeStartDate = datetime.datetime.now(),
                                            centralManagementStartDate = None,
                                            archiveStartDate = None,
                                            userID = request.user
                                      )
                                criterionsList.append(Criterion(
                                                                documentID = newDocument,
                                                                field1 = fields[0],
                                                                field2 = fields[1],
                                                                field3 = fields[2],
                                                                field4 = fields[3],
                                                                field5 = fields[4],
                                                                field6 = fields[5],
                                                                field7 = fields[6],
                                                                field8 = fields[7],
                                                                field9 = fields[8],
                                                                field10 = fields[9],
                                                                field11 = fields[10],
                                                                field12 = fields[11],
                                                           )
                                                )
                            Criterion.objects.bulk_create(criterionsList)
                return render_to_response('create/success.html',locals(), context)

    class createNewDoc(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            return render_to_response('create/new.html', context)

        @method_decorator(login_required)
        def post(self,request):
            context = RequestContext(request)
            fields = {}
            for i in range(1,13):
                fields['field' + str(i)] = request.POST.get('field' + str(i), '')
            newDocument = Document.objects.create(
                                                        active = True,
                                                        status = 'in-warehouse',
                                                        location = 'storage 1',
                                                        officeStartDate = datetime.datetime.now(),
                                                        centralManagementStartDate = None,
                                                        archiveStartDate = None,
                                                        userID = request.user
                                                  )
            criterionsList = []
            for eachField in fields:
                criterionsList.append(Criterion(
                                                documentID = newDocument,
                                                field1 = fields['field1'],
                                                field2 = fields['field2'],
                                                field3 = fields['field3'],
                                                field4 = fields['field4'],
                                                field5 = fields['field5'],
                                                field6 = fields['field6'],
                                                field7 = fields['field7'],
                                                field8 = fields['field8'],
                                                field9 = fields['field9'],
                                                field10 = fields['field10'],
                                                field11 = fields['field11'],
                                                field12 = fields['field12'],
                                           )
                                )
            Criterion.objects.bulk_create(criterionsList)
            return render_to_response ('create/success.html', context)

    class index(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            return render_to_response('main/office_main.html', locals(), context)