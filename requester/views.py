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


class Requester(View):
    class requestDocument(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            return render_to_response('return_requests/search.html', context)

        @method_decorator(login_required)
        def post(self,request):
            context = RequestContext(request)
            fields={}
            for i in range(1,13):
                fields['field' + str(i)] = request.POST.get('field' + str(i), '')
            searchButton = request.POST.get('searchButton', '')
            requestSubmit = request.POST.get('requestSubmit', '')
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
                                                            Q(field9__icontains = fields['field10']),
                                                            Q(field9__icontains = fields['field11']),
                                                            Q(field9__icontains = fields['field12']),
                                                            Q(documentID__status='in-warehouse')
                                                        )
                return render_to_response('return_requests/list.html', locals(), context)
            elif requestSubmit != '':
                pass
                #TODO
                # requestedDocuments = request.POST.get('requestedDocuments', '').split(',')
                # if len(requestedDocuments) == 1 and requestDocument[0] != '':

                #     newProtocol = Protocols.objects.create(
                #                                                 userID = request.user,
                #                                                 requestDate = datetime.datetime.now(),
                #                                                 fromLocation = criterionObject.documentID.location,
                #                                                 toLocation = 'requester', # requester
                #                                             )
                #     for eachDocument in requestedDocuments:
                #         currentDocument = Document.objects.get(id=int(eachDocument))
                #         requestList.append(Requests(
                #                                         documentID = currentDocument),
                #                                         status = 'in-progress',
                #                                         protocolID = newProtocol
                #                                     )
                #                                 )
                #         if currentDocument.status == 'in-courier':
                #             requestList.pop()
                #             newProtocol.delete()
                #             return render_to_response('move/error_incorrect_documents.html', context)
                #         else:
                #             currentDocument.status = 'in-courier'
                #             currentDocument.save()




                #     response = HttpResponse(content_type='application/pdf')
                #     response['Content-Disposition'] = 'attachment; filename="Protocol-for-incorrects-' + str(datetime.datetime.now()) +'.pdf"'
                #     boxstyle = [
                #                     ('ALIGN',         (0,0), (-1,0), 'CENTER'),
                #                     ('ALIGN',         (0,1), (-1,-1), 'CENTER'),
                #                     ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                #                     ('TOPPADDING',    (0,0), (-1,-1), 1),
                #                     ('LEFTPADDING',   (0,0), (-1,-1), 10),
                #                     ('GRID',          (0,0), (-1,-1), 0.3, colors.black),
                #                     ('FONT',          (0,0), (-1,0),  'b', 10),
                #                     ('FONT',          (0,1), (-1,-1),  'n', 10),
                #                 ]
                #     boxText =   [
                #             [u'Документ (критерии)', u'Забележка']
                #         ]

                #     boxCols = [12*cm, 5*cm]
                #     signBoxCols = [6*cm,3*cm,6*cm]
                #     signBoxStyle = [
                #                     ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
                #                     ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                #                     ('FONT',          (0,0), (-1,-1),  'n', 10)
                #                     ]

                #     criteriaFront = ''
                #     for eachRequest in requestedDocuments:
                #         criterionObject = Criterion.objects.get(documentID = int(eachRequest))
                #         criteriaFront += 'Име на регион: ' + criterionObject.field1 + '<br/>'
                #         criteriaFront += 'Име на клон: ' + criterionObject.field2 + '<br/>'
                #         criteriaFront += 'Клиентски номер: ' + criterionObject.field3 + '<br/>'
                #         criteriaFront += 'ЕИК/БУЛСТАТ: ' + criterionObject.field4 + '<br/>'
                #         criteriaFront += 'Име на клиент: ' + criterionObject.field5 + '<br/>'
                #         criteriaFront += 'Дата на договор: ' + criterionObject.field6 + '<br/>'
                #         criteriaFront += 'Номер на сметка: ' + criterionObject.field7 + '<br/>'
                #         criteriaFront += 'Размер на кредит: ' + criterionObject.field8 + '<br/>'
                #         criteriaFront += 'Валута: ' + criterionObject.field9 + '<br/>'
                #         criteriaFront += 'КИ идентификатор: ' + criterionObject.field10 + '<br/>'
                #         criteriaFront += 'Вид на документ: ' + criterionObject.field11 + '<br/>'
                #         criteriaFront += 'Описание: ' + criterionObject.field12 + '<br/>'

                #     header = Paragraph(u''' <strong> ПРИЛОЖЕНИЕ КЪМ ПРОТОКОЛ: (%s) </strong>'''%(str(requestObject.protocolID.id).zfill(5)),styleBoldCenter)
                #     textBeforeTable = Paragraph(u'''Долуописаните документи бяха предадени на заявител от ДСК.
                #         ''',styleNormal)
                #     boxText.append([
                #         Paragraph(criteriaFront,styleCenter),
                #         Paragraph('', styleCenter)
                #         ])
                #     textUnderTable = Paragraph(u'''Настоящия протокол се подписва в два еднакви екземпляра,
                #      по един за всяка от страните и се прикрепя към единия протокол и се изпраща обратно за другия.<br/><br/>
                #         ''', styleNormal)
                #     signBox = [
                #         [u'Дата: ' + datetime.datetime.now().strftime("%d.%m.%Y")+u'г.', u'', u''],
                #         [u'', u''],
                #         [u'ПРИЕЛ: ....................................',  u'',  u'ПРЕДАЛ: .....................................'],
                #         [u'Име:  .........................................',  u'',  u'Име: ..............................................'],
                #     ]
                #     cfs=[Spacer(0, 0.3*cm),
                #         header,
                #         Spacer(0, 0.3*cm),
                #         textBeforeTable,
                #         Spacer(0, 0.3*cm),
                #         Table(boxText, style=boxstyle, colWidths=boxCols),
                #         Spacer(0, 0.3*cm),
                #         textUnderTable,
                #         Spacer(0, 0.3*cm),
                #         Table(signBox, style=signBoxStyle, colWidths=signBoxCols),
                #         Spacer(0, 0.5*cm),
                #         Paragraph(u'________________________________________________________________________________' , styleNormal),
                #         Spacer(0, 0.3*cm),
                #         header,
                #         Spacer(0, 0.3*cm),
                #         textBeforeTable,
                #         Spacer(0, 0.3*cm),
                #         Table(boxText, style=boxstyle, colWidths=boxCols),
                #         Spacer(0, 0.3*cm),
                #         textUnderTable,
                #         Spacer(0, 0.3*cm),
                #         Table(signBox, style=signBoxStyle, colWidths=signBoxCols),
                #         Spacer(0, 0.3*cm),
                #          ]
                #     self.RequestTemplate(response, bottomMargin=1.3*cm, topMargin=1.3*cm).build(cfs)
                #     return response









        

    class index(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            return render_to_response('main/requester_main.html', locals(), context)