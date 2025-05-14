from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    return HttpResponse("<h1>Welcome to NEXO ING2</h1>")

def hello(request,username):
    return HttpResponse("<h2>Hello, %s. You're at the NEXO ING2 index.</h2>" % username)
