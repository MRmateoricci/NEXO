from datetime import datetime
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
from datetime import date
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .models import SolicitudReserva
from django.contrib import messages

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
        fecha_inicio_str = request.POST.get('fecha_inicio')
        fecha_fin_str = request.POST.get('fecha_fin')

        if not fecha_inicio_str or not fecha_fin_str:
            return JsonResponse({'error': 'Debés completar ambas fechas.'}, status=400)

        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()

            dias = (fecha_fin - fecha_inicio).days
            if dias <= 0:
                return JsonResponse({'error': 'La fecha de fin debe ser posterior a la de inicio.'}, status=400)

            monto_total = dias * inmueble.precio_diario

            reserva = SolicitudReserva.objects.create(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                inquilino=usuario_principal,
                inmueble=inmueble,
                estado='pendiente',
                monto_total=monto_total
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
            inquilinos_nuevos_json = request.POST.get('inquilinos_nuevos')
            if inquilinos_nuevos_json:
                try:
                    inquilinos_nuevos = json.loads(inquilinos_nuevos_json)
                    if not isinstance(inquilinos_nuevos, list):
                        inquilinos_nuevos = [inquilinos_nuevos]
                except json.JSONDecodeError:
                    inquilinos_nuevos = []

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
                'redirect_url': '/inmueble/listar?reserva=ok'
            })

        except Exception as e:
            return JsonResponse({
                'error': f'Error al crear la reserva: {str(e)}'
            }, status=500)

    return render(request, 'crear_reserva.html', {
        'fechas_ocupadas': fechas_ocupadas,
        'dni_inquilino':request.user.dni,
        'min_dias_reserva': inmueble.minimo_dias_reserva,
        'max_dias_reserva': inmueble.maximo_dias_reserva,
    })

def eliminarReservaView(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        solicitud_id = data.get("solicitud_id")
        try:
            solicitud = SolicitudReserva.objects.get(id=solicitud_id)
            solicitud.estado = 'cancelada'
            solicitud.save()
            return JsonResponse({"success": True})
        except SolicitudReserva.DoesNotExist:
            return JsonResponse({"success": False, "error": "No existe"}, status=404)
    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)
# Create your views here.

#@user_passes_test(es_empleado)
def validarSolicitudReservaView(request):
    caducar_solicitudes_pendientes()
    actualizar_estado_reservas()
    solicitudesPendientes = SolicitudReserva.objects.filter(estado='pendiente').order_by('fecha_inicio')
    SolicitudesPendientesDePago = SolicitudReserva.objects.filter(estado='pendiente de pago').order_by('fecha_inicio')
    solicitudesConfirmadas = SolicitudReserva.objects.filter(estado='confirmada')
    solicitudesIniciadas = SolicitudReserva.objects.filter(estado='iniciada')
    solicitudesFinalizadas = SolicitudReserva.objects.filter(estado='finalizada')
    solicitudesCanceladas = SolicitudReserva.objects.filter(estado='cancelada')
    solicitudes = list(solicitudesPendientes) + list(SolicitudesPendientesDePago) + list(solicitudesConfirmadas) + list(solicitudesIniciadas) + list(solicitudesFinalizadas) + list(solicitudesCanceladas)
    
    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud_id')
        accion = request.POST.get('accion')
        print(f"accion recibida: {accion}")
        try:
            solicitud = SolicitudReserva.objects.get(id=solicitud_id)
            if accion == 'aceptar':
                messages.success(request, "Solicitud aceptada correctamente.")
                # Generar link de pago
                link_pago = request.build_absolute_uri(
                    reverse('pagar_reserva', args=[solicitud.id])
                )

                # Renderizar el contenido HTML del mail
                html_content = render_to_string('boton_pago.html', {
                    'usuario': solicitud.inquilino,
                    'url_pago': link_pago,
                })

                # Enviar correo con contenido HTML
                email = EmailMultiAlternatives(
                    subject='Tu reserva fue aprobada - Realizá el pago',
                    body='Tu solicitud fue aceptada. Ingresá al siguiente enlace para pagar.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[solicitud.inquilino.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

                solicitud.estado = 'pendiente de pago'

            elif accion == 'rechazar':
                messages.error(request, "Solicitud rechazada correctamente.")
                solicitud.estado = 'cancelada'

            solicitud.save()
        except SolicitudReserva.DoesNotExist:
            pass  # Manejo opcional del error

        # Recargar la página con las solicitudes pendientes
        solicitudesPendientes = SolicitudReserva.objects.filter(estado='pendiente').order_by('fecha_inicio')
        SolicitudesPendientesDePago = SolicitudReserva.objects.filter(estado='pendiente de pago').order_by('fecha_inicio')
        solicitudes = list(solicitudesPendientes) + list(SolicitudesPendientesDePago)  

    return render(request, 'validar_solicitud_reserva.html', {'solicitudes': solicitudes})

def verSolicitudesPendientesView(request, inquilino_id):
    # Mostrar todas las solicitudes de reserva y reservas del inquilino, sin importar el estado
    caducar_solicitudes_pendientes()
    actualizar_estado_reservas()
    inquilino = Usuario.objects.get(id=inquilino_id)
    solicitudesInquilino = SolicitudReserva.objects.filter(inquilino=inquilino)
    reservasInquilino = Reserva.objects.filter(inquilino=inquilino)
    solicitudes_y_reservas = list(solicitudesInquilino) + list(reservasInquilino)
    return render(request, 'ver_solicitudes_pendientes.html', {'solicitudes': solicitudesInquilino, 'hoy': date.today()})

#@user_passes_test(es_empleado)
def solicitudReservasEmpleadoView(request):
    # Mostrar todas las reservas
    caducar_solicitudes_pendientes()
    actualizar_estado_reservas()
    reservas = SolicitudReserva.objects.all()
    return render(request, 'solicitud_reserva_empleado.html', {'reservas': reservas})

from django.db.models import Q

def buscar_usuarios_view(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse([], safe=False)
    inquilinos = Usuario.objects.filter(
        rol='inquilino')
    usuarios = inquilinos.filter(
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

    # Validación de dueño
    if solicitud.inquilino != request.user:
        return render(request, 'pago_no_valido.html', {'mensaje': 'No tenés permiso para pagar esta solicitud.'})

    if solicitud.estado != 'pendiente de pago':
        return render(request, 'pago_no_valido.html', {'mensaje': 'Esta solicitud no está disponible para pago.'})

    if request.method == 'POST':
        numero = request.POST.get('numero', '').strip()
        vencimiento = request.POST.get('vencimiento', '').strip()
        cvv = request.POST.get('cvv', '').strip()

        # Validaciones básicas de formato
        if not (numero and vencimiento and cvv):
            return render(request, 'pagar_reserva.html', {'solicitud': solicitud, 'error': 'Completa todos los campos.'})

        if not numero.isdigit() or len(numero) != 16:
            return render(request, 'pagar_reserva.html', {'solicitud': solicitud, 'error': 'Número de tarjeta inválido. Debe tener 16 dígitos.'})

        if not cvv.isdigit() or len(cvv) not in [3, 4]:
            return render(request, 'pagar_reserva.html', {'solicitud': solicitud, 'error': 'CVV inválido. Debe tener 3 o 4 dígitos numéricos.'})

        # Validar vencimiento (MM/AA)
        try:
            vencimiento_dt = datetime.strptime(vencimiento, "%m/%y")
            ahora = datetime.now()
            if vencimiento_dt.year < ahora.year or (vencimiento_dt.year == ahora.year and vencimiento_dt.month < ahora.month):
                return render(request, 'pagar_reserva.html', {'solicitud': solicitud, 'error': 'La tarjeta está vencida.'})
        except ValueError:
            return render(request, 'pagar_reserva.html', {'solicitud': solicitud, 'error': 'Formato de vencimiento inválido. Usá MM/AA.'})

        # Validar que exista la tarjeta asociada al usuario
        tarjeta = TarjetaPago.objects.filter(
            numero=numero,
            vencimiento=vencimiento,
            cvv=cvv,
        ).first()

        if not tarjeta:
            return render(request, 'pagar_reserva.html', {'solicitud': solicitud, 'error': 'Datos de tarjeta inválidos'})

        # Validar saldo
        if tarjeta.saldo < solicitud.monto_total:
            return render(request, 'pagar_reserva.html', {'solicitud': solicitud, 'error': 'Saldo insuficiente.'})

        # Procesar pago
        tarjeta.saldo -= solicitud.monto_total
        tarjeta.save()

        solicitud.estado = 'confirmada'
        solicitud.save()

        PagoReserva.objects.create(solicitud=solicitud)

        return render(request, 'pago_exitoso.html', {'solicitud': solicitud})

    return render(request, 'pagar_reserva.html', {'solicitud': solicitud})

def confirmar_cancelacion_reserva_view(request, reserva_id):
    reserva = get_object_or_404(SolicitudReserva, id=reserva_id)
    inmueble = reserva.inmueble
    from datetime import date
    dias_anticipacion = (reserva.fecha_inicio - date.today()).days

    if dias_anticipacion >= 7:
        porcentaje = inmueble.devolucion_7dias_o_mas
    elif 2 <= dias_anticipacion < 7:
        porcentaje = inmueble.devolucion_7_a_2dias
    else:
        porcentaje = inmueble.devolucion_2_a_0dias

    if request.method == "POST":
        reserva.estado = 'cancelada'
        reserva.save()
        # Redirige a la página de solicitudes del inquilino
        return redirect('ver_solicitudes_pendientes', inquilino_id=reserva.inquilino.id)


    from decimal import Decimal

    monto = reserva.monto_total * (Decimal(porcentaje) / Decimal('100'))
    return render(request, 'confirmar_cancelacion.html', {
        'reserva': reserva,
        'porcentaje_reintegro': int(monto),
        'dias_anticipacion': dias_anticipacion,
        'inquilino_id': reserva.inquilino.id,
    })

from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncDate

def caducar_solicitudes_pendientes():
    hace_un_dia = timezone.now().date() - timedelta(days=2)
    print(hace_un_dia)
    print(timezone.now().date())
    canceladas = SolicitudReserva.objects.filter(
        estado__in=['pendiente', 'pendiente de pago'],
        fecha_solicitud__lte=hace_un_dia  # 👈 hace más de 1 día calendario
    ).update(estado='cancelada')

    print(f"Se cancelaron {canceladas} solicitudes.")

def actualizar_estado_reservas():
    hoy = timezone.now().date()

    reservas_confirmadas = SolicitudReserva.objects.filter(estado='confirmada')
    for reserva in reservas_confirmadas:
        if hoy >= reserva.fecha_inicio and hoy <= reserva.fecha_fin:
            if reserva.estado != 'iniciada':
                reserva.estado = 'iniciada'
                reserva.save()
        elif hoy > reserva.fecha_fin:
            if reserva.estado != 'finalizada':
                reserva.estado = 'finalizada'
                reserva.save()