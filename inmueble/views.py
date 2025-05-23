from django.shortcuts import render
from .models import Inmueble

def listar_inmuebles(request):
    inmuebles = Inmueble.objects.all()
    return render(request, 'inmueble/listar.html', {'inmuebles' : inmuebles})