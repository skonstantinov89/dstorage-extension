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


class LoginClass(View):
    class Index(View):
        def get(self, request):
            context = RequestContext(request)
            if request.user.is_authenticated():
                return redirect('home')
            else:
                return redirect('login')
    class Home(View):
        def is_office_user(self,user):
            return user.groups.filter(name='office').exists()
        def is_central_user(self,user):
            return user.groups.filter(name='central-management').exists()

        def get(self, request):
            context = RequestContext(request)
            if request.user.is_authenticated():
                if self.is_office_user(request.user):
                    return redirect('/office')
                elif self.is_central_user(request.user):
                    return redirect('/central-management')

    class Login(View):
        def get(self, request):
            context = RequestContext(request)
            return render_to_response('base.html', context)
        def post(self,request):
            context = RequestContext(request)
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username = username, password = password)
            error = ''
            if user != None:
                login(request, user)
                error=''
                return redirect('/home', context)
            else:
                logout(request)
                error = 'Невалидно потребителско име или парола'
                return render_to_response('base.html', {'error': error}, context)

    class Logout(View):
        def get(self, request):
            logout(request)
            return redirect('/')
