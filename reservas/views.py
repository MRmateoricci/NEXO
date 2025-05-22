from django.shortcuts import render
from django.views import View
from .models import Reserva, SolicitudReserva
from django.http import JsonResponse, HttpResponse
from . import forms
from usuarios.models import Usuario
from inmueble.models import Inmueble

def ReservasView(request):
    return HttpResponse('pepe')

def CrearReservaView(request):
    if request.method == 'POST':
        form = forms.crearReservaForm(request.POST)
        if form.is_valid():
            # Aquí puedes procesar los datos del formulario
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
            # Guardar la reserva en la base de datos o realizar otra acción
            usuario = Usuario.objects.get(id = 1)
            inmueble = Inmueble.objects.get(id = 1)
            reserva = SolicitudReserva(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                inquilino=usuario,
                inmueble=inmueble  # Asumiendo que el usuario está autenticado
            )
            reserva.save()
            return JsonResponse({'success': True})
        else:
            return render(request, 'crear_reserva.html', {'crear_reserva': form})
    else:      
        return render(request, 'crear_reserva.html', {'crear_reserva': forms.crearReservaForm()})
    
def EliminarReservaView(request):
    #usuario = request.user  # Usuario autenticado
    usuario = Usuario.objects.get(id=1)  # Cambia esto por el usuario autenticado
    reservas = SolicitudReserva.objects.filter(inquilino=usuario)

    if request.method == 'POST':
        ids_a_eliminar = request.POST.getlist('reservas')
        SolicitudReserva.objects.filter(id__in=ids_a_eliminar, inquilino=usuario).delete()
        return render(request, 'eliminar_reserva.html', {
            'reservas': SolicitudReserva.objects.filter(inquilino=usuario),
            'mensaje': 'Reservas eliminadas correctamente.'
        })

    return render(request, 'eliminar_reserva.html', {'reservas': reservas})
# Create your views here.
