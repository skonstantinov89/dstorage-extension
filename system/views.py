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
        def is_office_user(user):
            return user.groups.filter(name='office').exists()
        def is_central_user(user):
            return user.groups.filter(name='central-management').exists()

        def get(self, request):
            context = RequestContext(request)
            if request.user.is_authenticated():
                if is_office_user(request.user):
                    return redirect('office')
                elif is_central_user(request.user):
                    return redirect('central-management')

    class Login(View):
        def get(self, request):
            context = RequestContext(request)
            return render_to_response('base.html', context)
        def post(self,request):
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username = username, password = password)
            print ('user: '),
            print (user)
            error = ''
            if user is not None:
                print('hey Login -> post')
                login(request)
                return redirect('/home')
            else:
                logout(request)
                error = 'Невалидно потребителско име или парола'
                return render_to_response('base.html', {'error': error})

    class Logout(View):
        def get(self, request):
            logout(request)
            return redirect('/')
