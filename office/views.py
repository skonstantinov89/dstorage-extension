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

from system.models import Document, Requests, Criterion, Files
from office.forms import DocumentForm
import datetime

class Office(View):
    class createBulk(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            form = DocumentForm() # A empty, unbound form
            return render_to_response ('create/bulk.html',{'form': form}, context)


        @method_decorator(login_required)
        def post(self, request):
            context = RequestContext(request)
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                newdoc = Files(docfile = request.FILES['docfile'])
                newdoc.save()
                return render_to_response('create/success.html',{'form':form}, context)

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

    class Index(View):
        @method_decorator(login_required)
        def get(self, request):
            context = RequestContext(request)
            return render_to_response('main/office_main.html', context)
        # def post(self, request):
        #   context = RequestContext(request)
        #   return render_to_response('base.html', context)