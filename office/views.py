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

class Office(View):
	class createNewDoc(View):
		@method_decorator(login_required)
		def get(self, request):
			context = RequestContext(request)
			return render_to_response('create/new.html', context)

		@method_decorator(login_required)
		def post(self,request):
			field1 = request.POST.get('field1', '')
			field2 = request.POST.get('field2', '')
			field3 = request.POST.get('field3', '')
			field4 = request.POST.get('field4', '')
			field5 = request.POST.get('field5', '')
			field6 = request.POST.get('field6', '')
			field7 = request.POST.get('field7', '')
			field8 = request.POST.get('field8', '')
			field8 = request.POST.get('field9', '')

			

	class Index(View):
		@method_decorator(login_required)
		def get(self, request):
			context = RequestContext(request)
			return render_to_response('base.html', context)
		# def post(self, request):
		# 	context = RequestContext(request)
		# 	return render_to_response('base.html', context)