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

from system.models import Document, Requests, Criterion, Files
from office.forms import DocumentForm
import datetime, codecs, csv

class Office(View):
    class moveToCentral(View):
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
            searchButton = request.POST.get('searchButton', False)
            if searchButton:
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
            else:
                centralDocuments = request.POST.get('centralDocuments', '')
                archiveDocuments = request.POST.get('archiveDocuments', '')
                requestList = []
                protocolList = []
                if centralDocuments:
                    newProtocol = Protocols.objects.create(
                                                userID = request.user,
                                                requestDate = datetime.datetime.now(),
                                                fromLocation = 'storage 1', # office
                                                toLocation = 'storage 2', # central
                                            )
                    for eachDocument in centralDocuments:
                        requestList.append(Requests(
                                                        documentID = Document.objects.get(id=int(eachDocument)),
                                                        status = 'in-progress',
                                                        protocolID = newProtocol
                                                   )
                                            )
                    Requests.objects.bulk_create(requestList)
                    for eachRequest in requestList:
                        protocolList.append(Protocols(
                                                        requestID = eachRequest
                                                    )
                                            )
                    Protocols.objects.bulk_create(protocolList)


                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="Protocol-' + barCode +'.pdf"'
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

                    boxCols = [5*cm,12*cm]
                    signBoxCols = [6*cm,3*cm,6*cm]
                    signBoxStyle = [
                                    ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
                                    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                                    ('FONT',          (0,0), (-1,-1),  'n', 10)
                                    ]

                    requestObject.status = 'in-rogress'
                    requestObject.userID = request.user
                    requestObject.DoneDate = datetime.datetime.now()
                    requestObject.save()
                    boxText =   [
                                    [u'Проект', u'Архивна Единица']
                                ]
                    requestCode = requestObject.id
                    requestDate = requestObject.RequestDate
                    criteriaData = criteria.objects.filter(archiveUnitID=requestObject.archiveUnitID)
                    criteriaFront = ''
                    for eachCriterion in criteriaData:
                        criteriaFront += eachCriterion.criteriaTypeID.name + ': ' + eachCriterion.value + '<br/>'
                    barCode =  str('R') + str(requestObject.id).zfill(7)

                    userObject = User.objects.get(id=requestObject.userID.id)
                    header = Paragraph(u''' <strong> ПРИЕМО-ПРЕДАВАТЕЛЕН ПРОТОКОЛ
                    ЗА ПРЕДАВАНЕ НА ДОКУМЕНТИ  (%s) </strong>'''%(barCode),styleBoldCenter)
                    textBeforeTable = Paragraph(u'''Долуподписаният …................................................................, представител на ДСК предаде
                    на …............................................................, представител на ДСК следната архивна единица:
                        '''%(requestObject.clientName),styleNormal)
                    boxText.append([
                        Paragraph(requestObject.projectName,styleCenter),
                        Paragraph(criteriaFront,styleCenter)
                        ])
                    textUnderTable = Paragraph(u'''Настоящия протокол се подписва в два еднакви екземпляра, по един за всяка от страните.<br/><br/>
                        ''', styleNormal)
                    signBox = [

                        [u'Дата: ' + datetime.datetime.now().strftime("%d.%m.%Y")+u'г.', u'', u''],
                        [u'', u''],

                        [u'ПРИЕЛ: ....................................',  u'',  u'ПРЕДАЛ: .....................................'],

                        [u'Име:  .........................................',  u'',  u'Име: ..............................................'],

                    ]
                    RequestBarcode = createBarcodeDrawing('Code128', value=barCode, humanReadable=1)
                    cfs=[Spacer(0, 0.5*cm),
                        RequestBarcode,
                        Spacer(0, 0.5*cm),
                        header,
                        Spacer(0, 0.5*cm),
                        textBeforeTable,
                        Spacer(0, 0.5*cm),
                        Table(boxText, style=boxstyle, colWidths=boxCols),
                        Spacer(0, 0.5*cm),
                        textUnderTable,
                        Spacer(0, 0.5*cm),
                        Table(signBox, style=signBoxStyle, colWidths=signBoxCols),
                        Spacer(0, 0.7*cm),
                        Paragraph(u'________________________________________________________________________________' , styleNormal),
                        Spacer(0, 0.5*cm),
                        RequestBarcode,
                        Spacer(0, 0.5*cm),
                        header,
                        Spacer(0, 0.5*cm),
                        textBeforeTable,
                        Spacer(0, 0.5*cm),
                        Table(boxText, style=boxstyle, colWidths=boxCols),
                        Spacer(0, 0.5*cm),
                        textUnderTable,
                        Spacer(0, 0.5*cm),
                        Table(signBox, style=signBoxStyle, colWidths=signBoxCols),
                        Spacer(0, 0.7*cm),
                         ]
                    RequestTemplate(response, bottomMargin=1.3*cm, topMargin=1.3*cm).build(cfs)
                    return response


                    if archiveDocuments:
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="Protocol-' + datetime.datetime.now() +'.pdf"'
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

                    boxCols = [5*cm,12*cm]
                    signBoxCols = [6*cm,3*cm,6*cm]
                    signBoxStyle = [
                                    ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
                                    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                                    ('FONT',          (0,0), (-1,-1),  'n', 10)
                                    ]

                    requestObject.status = 'waiting-return-courier'
                    requestObject.operatorStartID = request.user
                    requestObject.DoneDate = datetime.datetime.now()
                    requestObject.save()
                    boxText =   [
                                    [u'Проект', u'Архивна Единица']
                                ]
                    requestCode = requestObject.id
                    requestDate = requestObject.RequestDate
                    criteriaData = criteria.objects.filter(archiveUnitID=requestObject.archiveUnitID)
                    criteriaFront = ''
                    for eachCriterion in criteriaData:
                        criteriaFront += eachCriterion.criteriaTypeID.name + ': ' + eachCriterion.value + '<br/>'
                    barCode =  str('R') + str(requestObject.id).zfill(7)

                    userObject = User.objects.get(id=requestObject.userID.id)
                    header = Paragraph(u''' <strong> ПРИЕМО-ПРЕДАВАТЕЛЕН ПРОТОКОЛ
                    ЗА ПРЕДАВАНЕ НА ДОКУМЕНТИ  (%s) </strong>'''%(barCode),styleBoldCenter)
                    textBeforeTable = Paragraph(u'''Долуподписаният …................................................................, представител на %s предаде
                    на …............................................................, представител на ДСК следната архивна единица:
                        '''%(requestObject.clientName),styleNormal)
                    boxText.append([
                        Paragraph(requestObject.projectName,styleCenter),
                        Paragraph(criteriaFront,styleCenter)
                        ])
                    textUnderTable = Paragraph(u'''Настоящия протокол се подписва в два еднакви екземпляра, по един за всяка от страните.<br/><br/>
                        ''', styleNormal)
                    signBox = [

                        [u'Дата: ' + datetime.datetime.now().strftime("%d.%m.%Y")+u'г.', u'', u''],
                        [u'', u''],

                        [u'ПРИЕЛ: ....................................',  u'',  u'ПРЕДАЛ: .....................................'],

                        [u'Име:  .........................................',  u'',  u'Име: ..............................................'],

                    ]
                    RequestBarcode = createBarcodeDrawing('Code128', value=barCode, humanReadable=1)
                    cfs=[Spacer(0, 0.5*cm),
                        RequestBarcode,
                        Spacer(0, 0.5*cm),
                        header,
                        Spacer(0, 0.5*cm),
                        textBeforeTable,
                        Spacer(0, 0.5*cm),
                        Table(boxText, style=boxstyle, colWidths=boxCols),
                        Spacer(0, 0.5*cm),
                        textUnderTable,
                        Spacer(0, 0.5*cm),
                        Table(signBox, style=signBoxStyle, colWidths=signBoxCols),
                        Spacer(0, 0.7*cm),
                        Paragraph(u'________________________________________________________________________________' , styleNormal),
                        Spacer(0, 0.5*cm),
                        RequestBarcode,
                        Spacer(0, 0.5*cm),
                        header,
                        Spacer(0, 0.5*cm),
                        textBeforeTable,
                        Spacer(0, 0.5*cm),
                        Table(boxText, style=boxstyle, colWidths=boxCols),
                        Spacer(0, 0.5*cm),
                        textUnderTable,
                        Spacer(0, 0.5*cm),
                        Table(signBox, style=signBoxStyle, colWidths=signBoxCols),
                        Spacer(0, 0.7*cm),
                         ]
                    RequestTemplate(response, bottomMargin=1.3*cm, topMargin=1.3*cm).build(cfs)
                    return response




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
                        if len(eachElement) != 9:
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
            for i in range(1,10):
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
                                           )
                                )
            Criterion.objects.bulk_create(criterionsList)
            return render_to_response ('create/success.html', context)

    class index(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            return render_to_response('main/office_main.html', locals(), context)