from django.shortcuts import render
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
# Create your views here.
