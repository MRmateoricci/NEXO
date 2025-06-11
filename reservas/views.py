import json
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .models import Inquilino, PagoReserva, Reserva, SolicitudReserva, TarjetaPago
from django.http import JsonResponse, HttpResponse
from . import forms
from usuarios.models import Usuario
from inmueble.models import Inmueble
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils import timezone

from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

def es_empleado(usuario):
    return getattr(usuario, 'rol', '').lower() == 'empleado'


def ReservasView(request):
    return HttpResponse('pepe')

def crearReservaView(request, inmueble_id):
    inmueble = get_object_or_404(Inmueble, id=inmueble_id)
    usuario_principal = request.user

    # Obtener fechas ocupadas
    reservas = SolicitudReserva.objects.filter(inmueble=inmueble).exclude(estado='cancelada')
    fechas_ocupadas = [
        {'fecha_inicio': r.fecha_inicio.strftime('%Y-%m-%d'), 'fecha_fin': r.fecha_fin.strftime('%Y-%m-%d')}
        for r in reservas
    ]

    if inmueble.fecha_inicio_inactividad and inmueble.fecha_fin_inactividad:
        fechas_ocupadas.append({
            'fecha_inicio': inmueble.fecha_inicio_inactividad.strftime('%Y-%m-%d'),
            'fecha_fin'   : inmueble.fecha_fin_inactividad.strftime('%Y-%m-%d'),
        })


    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')

        if not fecha_inicio or not fecha_fin:
            return JsonResponse({'error': 'Debés completar ambas fechas.'}, status=400)

        try:
            # Crear la reserva
            reserva = SolicitudReserva.objects.create(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                inquilino=usuario_principal,
                inmueble=inmueble,
                estado='pendiente'
            )

            # Procesar inquilinos existentes
            inquilinos_existentes_ids = request.POST.getlist('inquilinos_existentes', [])
            for usuario_id in inquilinos_existentes_ids:
                usuario = get_object_or_404(Usuario, id=usuario_id)
                inquilino, _ = Inquilino.objects.get_or_create(
                    usuario=usuario,
                    defaults={
                        'nombre': usuario.get_full_name(),
                        'dni': 'N/A',
                        'edad': 0,
                        'creado_por': usuario_principal
                    }
                )
                reserva.inquilinos.add(inquilino)

            # Procesar inquilinos nuevos
            inquilinos_nuevos = []
            inquilinos_nuevos_json = request.POST.get('inquilinos_nuevos')
            if inquilinos_nuevos_json:
                try:
                    inquilinos_nuevos = json.loads(inquilinos_nuevos_json)
                    if not isinstance(inquilinos_nuevos, list):
                        inquilinos_nuevos = [inquilinos_nuevos]
                except json.JSONDecodeError:
                    pass

            for data in inquilinos_nuevos:
                inquilino = Inquilino.objects.create(
                    nombre=data.get('nombre', ''),
                    dni=data.get('dni', ''),
                    edad=int(data.get('edad', 0)),
                    creado_por=usuario_principal
                )
                reserva.inquilinos.add(inquilino)

            return JsonResponse({
                'success': True,
                'redirect_url': '/inmueble/listar?reserva=ok'  # URL a la que redirigir
            })

        except Exception as e:
            return JsonResponse({
                'error': f'Error al crear la reserva: {str(e)}'
            }, status=500)

    # GET
    return render(request, 'crear_reserva.html', {
        'fechas_ocupadas': fechas_ocupadas
    }) 

        
    
def eliminarReservaView(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        solicitud_id = data.get("solicitud_id")
        try:
            solicitud = SolicitudReserva.objects.get(id=solicitud_id)
            solicitud.delete()
            return JsonResponse({"success": True})
        except SolicitudReserva.DoesNotExist:
            return JsonResponse({"success": False, "error": "No existe"}, status=404)
    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)
# Create your views here.

#@user_passes_test(es_empleado)
def validarSolicitudReservaView(request):
    # Mostrar solo solicitudes pendientes
    solicitudes = SolicitudReserva.objects.filter(estado='pendiente', fecha_inicio__gt= timezone.now().date()).order_by('fecha_inicio')

    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud_id')
        accion = request.POST.get('accion')
        try:
            solicitud = SolicitudReserva.objects.get(id=solicitud_id)
            if accion == 'aceptar':
                # Generar link de pago
                link_pago = request.build_absolute_uri(
                    reverse('pagar_reserva', args=[solicitud.id])
                )

                # Enviar mail al inquilino
                send_mail(
                    subject='Tu reserva fue aprobada - Realizá el pago',
                    message=f'Tu solicitud fue aceptada. Podés pagarla ingresando aquí:\n{link_pago}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[solicitud.inquilino.email]
                )
                solicitud.estado = 'pendiente de pago'
            elif accion == 'rechazar':
                solicitud.estado = 'cancelada'
            solicitud.save()
        except SolicitudReserva.DoesNotExist:
            pass  # Puedes manejar el error si quieres

        # Recargar la página para mostrar el cambio
        solicitudes = SolicitudReserva.objects.filter(estado='pendiente')

    return render(request, 'validar_solicitud_reserva.html', {'solicitudes': solicitudes})

def verSolicitudesPendientesView(request, inquilino_id):
    # Mostrar solo solicitudes pendientes
    solicitudes = SolicitudReserva.objects.filter(estado='pendiente')
    inquilino = Usuario.objects.get(id=inquilino_id)
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

from .models import TarjetaPago, PagoReserva

def pagar_reserva_view(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudReserva, id=solicitud_id)

    if solicitud.estado != 'pendiente de pago':
        return render(request, 'pago_no_valido.html', {'mensaje': 'Esta solicitud no está disponible para pago.'})

    if request.method == 'POST':
        numero = request.POST.get('numero')
        vencimiento = request.POST.get('vencimiento')
        cvv = request.POST.get('cvv')

        if not (numero and vencimiento and cvv):
            return render(request, 'pagar_reserva.html', {'solicitud': solicitud, 'error': 'Completa todos los campos.'})

        # Verificar si la tarjeta existe
        if TarjetaPago.objects.filter(numero=numero, vencimiento=vencimiento, cvv=cvv).exists():
            # Marcar la solicitud como pagada
            solicitud.estado = 'pagada'
            solicitud.save()

            # Guardar el pago (si tenés modelo PagoReserva)
            PagoReserva.objects.create(solicitud=solicitud)

            return render(request, 'pago_exitoso.html', {'solicitud': solicitud})
        else:
            return render(request, 'pagar_reserva.html', {'solicitud': solicitud, 'error': 'Datos de tarjeta inválidos.'})

    return render(request, 'pagar_reserva.html', {'solicitud': solicitud})
