import json
from django.shortcuts import get_object_or_404, render
from django.views import View
from .models import Inquilino, Reserva, SolicitudReserva
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
    inmueble = get_object_or_404(Inmueble, id=inmueble_id)
    usuario_principal = request.user  # Asume que el usuario está autenticado

    # Obtener fechas ocupadas (lógica existente)
    reservas = SolicitudReserva.objects.filter(inmueble=inmueble).exclude(estado='cancelada')
    fechas_ocupadas = [
        {'fecha_inicio': r.fecha_inicio.strftime('%Y-%m-%d'), 'fecha_fin': r.fecha_fin.strftime('%Y-%m-%d')}
        for r in reservas
    ]

    if request.method == 'POST':
        form = forms.crearReservaForm(request.POST)
        if form.is_valid():
            # Crear la reserva base
            reserva = SolicitudReserva(
                fecha_inicio=form.cleaned_data['fecha_inicio'],
                fecha_fin=form.cleaned_data['fecha_fin'],
                inquilino=usuario_principal,
                inmueble=inmueble,
                estado='pendiente'
            )
            reserva.save()

            # Procesar inquilinos existentes (IDs de usuarios registrados)
            inquilinos_existentes_ids = request.POST.getlist('inquilinos_existentes', [])
            for usuario_id in inquilinos_existentes_ids:
                usuario = get_object_or_404(Usuario, id=usuario_id)
                inquilino, _ = Inquilino.objects.get_or_create(
                    usuario=usuario,
                    defaults={'nombre': usuario.get_full_name(), 'dni': 'N/A', 'edad': 0, 'creado_por': usuario_principal}
                )
                reserva.inquilinos.add(inquilino)

            # Recibir el JSON como string (un solo input con todos los nuevos inquilinos)
            inquilinos_nuevos_json = request.POST.get('inquilinos_nuevos', '[]')

            try:
                inquilinos_nuevos = json.loads(inquilinos_nuevos_json)
            except json.JSONDecodeError:
                inquilinos_nuevos = []

            # Asegurar que sea una lista, no un dict
            if isinstance(inquilinos_nuevos, dict):
                inquilinos_nuevos = [inquilinos_nuevos]

            # Crear los inquilinos
            for data in inquilinos_nuevos:
                inquilino = Inquilino.objects.create(
                    nombre=data.get('nombre', ''),
                    dni=data.get('dni', ''),
                    edad=int(data.get('edad', 0)),
                    creado_por=usuario_principal
                )
                reserva.inquilinos.add(inquilino)

            return JsonResponse({'success': True, 'reserva_id': reserva.id})

        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    else:
        # GET: Mostrar formulario con opciones de inquilinos
        usuarios_registrados = Usuario.objects.exclude(id=usuario_principal.id)  # Excluye al usuario actual
        return render(request, 'crear_reserva.html', {
            'crear_reserva_form': forms.crearReservaForm(),
            'fechas_ocupadas': fechas_ocupadas,
            'usuarios_registrados': usuarios_registrados,
        })
    
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

from django.db.models import Q

def buscar_usuarios_view(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse([], safe=False)

    usuarios = Usuario.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(username__icontains=query)
    ).exclude(id=request.user.id)[:10]

    resultados = [
        {
            'id': usuario.id,
            'text': f"{usuario.get_full_name()} ({usuario.email})",  # Texto que se mostrará en el dropdown
            'nombre': usuario.get_full_name(),
            'email': usuario.email
        }
        for usuario in usuarios
    ]

    return JsonResponse(resultados, safe=False)

def gestion_inquilinos_view(request, reserva_id):
    reserva = get_object_or_404(SolicitudReserva, id=reserva_id)
    
    if request.method == 'POST':
        # Lógica para agregar/eliminar inquilinos de una reserva existente
        pass
    
    # Obtener usuarios registrados para el select
    usuarios_registrados = Usuario.objects.exclude(id=request.user.id)
    
    return render(request, 'gestion_inquilinos.html', {
        'reserva': reserva,
        'usuarios_registrados': usuarios_registrados
    })