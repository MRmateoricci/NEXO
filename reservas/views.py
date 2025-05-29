from django.shortcuts import render
from django.views import View
from .models import Reserva, SolicitudReserva
from django.http import JsonResponse, HttpResponse
from . import forms
from usuarios.models import Usuario
from inmueble.models import Inmueble
from django.contrib.auth.decorators import user_passes_test

def es_empleado(usuario):
    return getattr(usuario, 'rol', '').lower() == 'empleado'


def ReservasView(request):
    return HttpResponse('pepe')

def crearReservaView(request, inmueble_id):
    inmueble = Inmueble.objects.get(id=inmueble_id)
    reservas = SolicitudReserva.objects.filter(
        inmueble=inmueble
    ).exclude(estado='cancelada')

    fechas_ocupadas = []
    for reserva in reservas:
        fechas_ocupadas.append({
            'fecha_inicio': reserva.fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': reserva.fecha_fin.strftime('%Y-%m-%d')
        })
    if request.method == 'POST':
        form = forms.crearReservaForm(request.POST)
        if form.is_valid():
            # Aquí puedes procesar los datos del formulario
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
            # Guardar la reserva en la base de datos o realizar otra acción
            usuario = Usuario.objects.get(id = 1)
            reserva = SolicitudReserva(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                inquilino=usuario,
                inmueble=inmueble  # Asumiendo que el usuario está autenticado
            )
            reserva.save()
            return JsonResponse({'success': True})
        else:
            return render(request, 'crear_reserva.html', {'crear_reserva': form,
            'fechas_ocupadas': fechas_ocupadas})
    else:      
        return render(request, 'crear_reserva.html', {'crear_reserva': forms.crearReservaForm(),
        'fechas_ocupadas': fechas_ocupadas})
    
def eliminarReservaView(request):
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

#@user_passes_test(es_empleado)
def validarSolicitudReservaView(request):
    # Mostrar solo solicitudes pendientes
    solicitudes = SolicitudReserva.objects.filter(estado='pendiente')

    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud_id')
        accion = request.POST.get('accion')
        try:
            solicitud = SolicitudReserva.objects.get(id=solicitud_id)
            if accion == 'aceptar':
                solicitud.estado = 'pendiente de pago'
            elif accion == 'rechazar':
                solicitud.estado = 'cancelada'
            solicitud.save()
        except SolicitudReserva.DoesNotExist:
            pass  # Puedes manejar el error si quieres

        # Recargar la página para mostrar el cambio
        solicitudes = SolicitudReserva.objects.filter(estado='pendiente')

    return render(request, 'validar_solicitud_reserva.html', {'solicitudes': solicitudes})

def verSolicitudesPendientesView(request):
    # Mostrar solo solicitudes pendientes
    solicitudes = SolicitudReserva.objects.filter(estado='pendiente')
    inquilino = Usuario.objects.get(id=1)
    solicitudesInquilino = solicitudes.filter(inquilino=inquilino)
    return render(request, 'ver_solicitudes_pendientes.html', {'solicitudes': solicitudesInquilino})

#@user_passes_test(es_empleado)
def solicitudReservasEmpleadoView(request):
    # Mostrar todas las reservas
    reservas = SolicitudReserva.objects.all()
    return render(request, 'solicitud_reserva_empleado.html', {'reservas': reservas})
