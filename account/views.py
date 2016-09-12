from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.core.validators import validate_email
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.text import slugify
from django.views.generic import View

from account.models import CustomUser


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']

        # check parameters
        if len(email) == 0 or len(password) == 0:
            context = {
                'error_message': "Isian tidak lengkap"
            }
            return render(request, 'login.html', context)

        # check email format
        try:
            validate_email(email)
        except ValidationError:
            context = {
                'error_message': "Format email salah"
            }
            return render(request, 'login.html', context)

        # check whether user is registered
        user = authenticate(username=email, password=password)
        if user is None:
            context = {
                'error_message': "Kombinasi email dan password tidak cocok"
            }
            return render(request, 'login.html', context)

        login(request, user)

        if user.is_staff:
            return HttpResponseRedirect(reverse_lazy('core-dashboard'))

        print reverse_lazy('ag-dashboard', current_app='agent')
        return HttpResponseRedirect(reverse_lazy('ag-dashboard'))


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse_lazy('login'))


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']

        # check parameters
        if len(email) == 0 or len(password) == 0 or len(confirm) == 0:
            context = {
                'email': email,
                'password': password,
                'confirm': confirm,
                'error_message': "Isian tidak lengkap"
            }
            return render(request, 'register.html', context)

        # check email format
        try:
            validate_email(email)
        except ValidationError:
            context = {
                'password': password,
                'confirm': confirm,
                'error_message': "Format email salah"
            }
            return render(request, 'register.html', context)

        # check password and confirm match
        if password != confirm:
            context = {
                'email': email,
                'error_message': "Password dan konfirmasi tidak cocok"
            }
            return render(request, 'register.html', context)

        # check user has been registered
        try:
            CustomUser.objects.get(email=email)
            context = {
                'password': password,
                'confirm': confirm,
                'error_message': "Email telah terdaftar"
            }
            return render(request, 'register.html', context)
        except CustomUser.DoesNotExist:
            pass

        # create new user
        user = CustomUser(email=email, password=make_password(password))
        user.save()

        login(request, user)

        return HttpResponseRedirect(reverse_lazy('feed'))


