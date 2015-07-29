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
            return render_to_response('main/office_main.html', context)