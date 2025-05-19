from django.shortcuts import render
from django.views import View
from .models import Reserva, SolicitudReserva
from django.http import JsonResponse, HttpResponse
from . import forms

def ReservasView(request):
    return HttpResponse('pepe')

def CrearReservaView(request):
    if request.method == 'POST':
        form = forms.crearReservaForm(request.POST)
        if form.is_valid():
            # Aquí puedes procesar los datos del formulario
            nombre = form.cleaned_data['nombre']
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
            descripcion = form.cleaned_data['descripcion']
            # Guardar la reserva en la base de datos o realizar otra acción
            return JsonResponse({'success': True})
        else:
            return render(request, 'crear_reserva.html', {'crear_reserva': form})
    else:      
        return render(request, 'crear_reserva.html', {'crear_reserva': forms.crearReservaForm()})

# Create your views here.
