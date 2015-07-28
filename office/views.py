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

            criteriaData = Criterion.objects.filter(documentID__status='in-warehouse')
            # documentData = list(Document.objects.filter(active=True).values_list('id', flat=True))
            documentData = Document.objects.select_related().filter(active=True)
            # criteriaData = 
            for eachField in fields:
                pass
                # TODO
            criteriaData=criteriaData.filter(
                                                Q(criteriaType = 'field1'), Q(criteriaValue__icontains = fields['field1']) |
                                                Q(criteriaType = 'field2'), Q(criteriaValue__icontains = fields['field2']) |
                                                Q(criteriaType = 'field3'), Q(criteriaValue__icontains = fields['field3']) |
                                                Q(criteriaType = 'field4'), Q(criteriaValue__icontains = fields['field4']) |
                                                Q(criteriaType = 'field5'), Q(criteriaValue__icontains = fields['field5']) |
                                                Q(criteriaType = 'field6'), Q(criteriaValue__icontains = fields['field6']) |
                                                Q(criteriaType = 'field7'), Q(criteriaValue__icontains = fields['field7']) |
                                                Q(criteriaType = 'field8'), Q(criteriaValue__icontains = fields['field8']) |
                                                Q(criteriaType = 'field9'), Q(criteriaValue__icontains = fields['field9']),
                                                Q(documentID__in = documentData)
                                            )


            print (criteriaData)
            docIDs = criteriaData.values_list('documentID', flat=True).distinct()

            criteriaData = criteriaData.order_by('documentID')

            frontData = []
            for eachDoc in docIDs:
                frontData.append({
                    'document': Document.objects.filter(id=eachDoc),
                    'fields': criteriaData.filter(documentID=eachDoc)
                    })
            return render_to_response('move/list.html', locals(), context)



    class preview(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            frontData = []
            documentData = Document.objects.filter(active=True)
            for eachDocument in documentData:
                frontData.append({
                    'document': eachDocument,
                    'fields': Criterion.objects.filter(documentID = eachDocument.id),
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
                                                                criteriaType = 'field1',
                                                                criteriaValue = fields[0],
                                                           )
                                                )
                                criterionsList.append(Criterion(
                                                                documentID = newDocument,
                                                                criteriaType = 'field2',
                                                                criteriaValue = fields[1],
                                                           )
                                                )
                                criterionsList.append(Criterion(
                                                                documentID = newDocument,
                                                                criteriaType = 'field3',
                                                                criteriaValue = fields[2],
                                                           )
                                                )
                                criterionsList.append(Criterion(
                                                                documentID = newDocument,
                                                                criteriaType = 'field4',
                                                                criteriaValue = fields[3],
                                                           )
                                                )
                                criterionsList.append(Criterion(
                                                                documentID = newDocument,
                                                                criteriaType = 'field5',
                                                                criteriaValue = fields[4],
                                                           )
                                                )
                                criterionsList.append(Criterion(
                                                                documentID = newDocument,
                                                                criteriaType = 'field6',
                                                                criteriaValue = fields[5],
                                                           )
                                                )
                                criterionsList.append(Criterion(
                                                                documentID = newDocument,
                                                                criteriaType = 'field7',
                                                                criteriaValue = fields[6],
                                                           )
                                                )
                                criterionsList.append(Criterion(
                                                                documentID = newDocument,
                                                                criteriaType = 'field8',
                                                                criteriaValue = fields[7],
                                                           )
                                                )
                                criterionsList.append(Criterion(
                                                                documentID = newDocument,
                                                                criteriaType = 'field9',
                                                                criteriaValue = fields[8],
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
                                                criteriaType = eachField,
                                                criteriaValue = fields[eachField],
                                           )
                                )
            Criterion.objects.bulk_create(criterionsList)
            return render_to_response ('create/success.html', context)

    class index(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            return render_to_response('main/office_main.html', context)