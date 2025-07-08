from django.shortcuts import render,redirect, get_object_or_404
from .models import Inmueble
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Reseña
@login_required
def eliminar_reseña(request, reseña_id):
    if request.method == 'POST':
        reseña = get_object_or_404(Reseña, id=reseña_id)
        if request.user.rol == "empleado":
            inmueble_id = reseña.inmueble.id
            reseña.delete()
            messages.success(request, "Reseña eliminada correctamente.")
            return redirect('ver_detalle_inmueble', inmueble_id=inmueble_id)
        else:
            messages.error(request, "No tienes permisos para eliminar esta reseña.")
            return redirect('ver_detalle_inmueble', inmueble_id=reseña.inmueble.id)
    else:
        return redirect('ver_detalle_inmueble', inmueble_id=reseña.inmueble.id)


def listar_inmuebles(request):
    # Parámetros GET (con valores por defecto y sanitización)
    filters = Q(activo=True)
    tipo = request.GET.get('tipo', '').strip()
    huespedes = request.GET.get('huespedes', '').strip()
    metros = request.GET.get('metros', '').strip()
    banos = request.GET.get('banos','').strip()

    # Filtrado
    if tipo:
        filters &= Q(tipo__iexact=tipo)
    if huespedes:
        try:
            filters &= Q(cantidad_huespedes__gte=int(huespedes))
        except ValueError:
            pass
    if metros:
        try:
            filters &= Q(metros_cuadrados__gte=float(metros))
        except ValueError:
            pass
    if banos:
        try:
            filters &= Q(banos__gte=int(banos))           
        except ValueError:
            pass

    inmuebles = Inmueble.objects.filter(filters)
    
    # Paginación
    paginator = Paginator(inmuebles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Choices para el template
    tipo_choices = Inmueble._meta.get_field('tipo').choices or []

    return render(request, 'inmueble/listar.html', {
        'page_obj': page_obj,
        'tipo': tipo,
        'huespedes': huespedes,
        'metros': metros,
        'tipo_choices': tipo_choices,
        'banos': banos,
    })


   

#HU ver disponibilidad de inmueble
from django.shortcuts import render, get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
import datetime
import json
from .models import Inmueble
from reservas.models import Reserva, SolicitudReserva # Importar el modelo Reserved

def ver_disponibilidad(request, inmueble_id):
    inmueble = get_object_or_404(Inmueble, id=inmueble_id)
    
    # Obtener reservas CONFIRMADAS de este inmueble (filtramos por estado)
    reservas = Reserva.objects.filter(
        inmueble=inmueble,
        estado='confirmada'  # Solo consideramos reservas confirmadas
    )
    
    # Generar lista de fechas ocupadas (YYYY-MM-DD)
    fechas_ocupadas = []
    for reserva in reservas:
        current_date = reserva.fecha_inicio
        while current_date <= reserva.fecha_fin:
            fechas_ocupadas.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
    
    # Eventos para FullCalendar
    eventos = [
        {
            'title': 'Ocupado',
            'start': fecha,
            'allDay': True,
            'color': 'red',
            'textColor': 'white'  # Opcional: mejora legibilidad
        } for fecha in fechas_ocupadas
    ]
    
    return render(request, 'inmueble/disponibilidad.html', {
        'inmueble': inmueble,
        'eventos_json': json.dumps(eventos, cls=DjangoJSONEncoder)
    })
from django.shortcuts import render, get_object_or_404, redirect
from .models import Inmueble, Reseña
from reservas.models import SolicitudReserva  # Asumiendo que tu modelo de reserva se llama así
from .forms import ReseñaForm
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

def ver_detalle_inmueble(request, inmueble_id):
    inmueble = get_object_or_404(Inmueble, pk=inmueble_id)
    puede_reseñar = SolicitudReserva.objects.filter(
        inquilino_id=request.user.id,
        inmueble_id=inmueble.id,
        estado='confirmada'
    ).exists()

    if request.method == 'POST' and puede_reseñar:
        form = ReseñaForm(request.POST)
        if form.is_valid():
            # Chequear si ya existe una reseña para este usuario e inmueble
            if Reseña.objects.filter(inmueble=inmueble, inquilino=request.user).exists():
                messages.error(request, "Ya has dejado una reseña para este inmueble.")            
            else:
                try:
                    reseña = form.save(commit=False)
                    reseña.inmueble = inmueble
                    reseña.inquilino = request.user
                    reseña.save()
                    return redirect('ver_detalle_inmueble', inmueble_id=inmueble.id)
                except IntegrityError:
                    messages.error(request, "Ya has dejado una reseña para este inmueble.")  
    else:
        form = ReseñaForm()

    reseñas = inmueble.resenas.all().order_by('-fecha_creacion')

    return render(request, 'inmueble/ver_detalle.html', {
        'inmueble': inmueble,
        'reseñas': reseñas,
        'form': form,
        'puede_reseñar': puede_reseñar,
    })

from .forms import AltaInmueble

def dar_alta_inmueble(request):
    if request.method == 'POST':
        formulario = AltaInmueble(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "inmueble dado de alta correctamente.")
            return redirect('listar_inmuebles')
    else:
        formulario = AltaInmueble()
    return render(request, 'inmueble/dar_alta.html', {'form': formulario})

from django.contrib import messages

def eliminar_inmueble(request, id):
    inmueble = get_object_or_404(Inmueble, pk=id)
    reservas = SolicitudReserva.objects.filter(inmueble=inmueble).exclude(estado='cancelada')
    if reservas.exists():
        messages.error(request,
            "El inmueble tiene solicitudes de reserva. No se puede darlo de baja."
        )
        return redirect('listar_inmuebles')

    if request.method == 'POST':
        inmueble.activo = False
        inmueble.estado = 'No disponible'
        inmueble.save()
        messages.success(request, "Inmueble dado de baja correctamente.")
        return redirect('listar_inmuebles')
    return render(request,'inmueble/confirmar_baja.html',{'inmueble': inmueble})

from .forms import EditarInmueble

def editar_inmueble(request, id):
    inmueble = get_object_or_404(Inmueble,pk=id)
    reservas = SolicitudReserva.objects.filter(inmueble=inmueble).exclude(estado='cancelada')
    if reservas.exists():
        messages.error(request, "El inmueble tiene solicitudes de reserva. No se pueden realizar cambios.")
        return redirect('listar_inmuebles')
    
    if request.method == "POST":
        form = EditarInmueble(request.POST, request.FILES, instance=inmueble)
        if form.is_valid():
            form.save()
            messages.success(request, "El inmueble se editó correctamente.")
            return redirect('listar_inmuebles')
    else:
        form = EditarInmueble(instance=inmueble)
    return render(request, 'inmueble/editar.html',{'form': form})

def listar_inmuebles_inactivos(request):
    inmuebles_inactivos = Inmueble.objects.filter(activo=False)
    
    # Paginación (igual que en listar activos, pero con el queryset inactivo)
    paginator = Paginator(inmuebles_inactivos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inmueble/listar_inactivos.html', {
        'page_obj': page_obj,
    })

def activar_inmueble(request, id):
    inmueble = get_object_or_404(Inmueble, pk=id)
    
    if request.method == 'POST':
        inmueble.activo = True
        inmueble.estado = 'Disponible'
        # Si usas campo 'estado', podrías volver a setearlo:
        # inmueble.estado = 'activo'
        inmueble.save()
        messages.success(request, "El inmueble ha sido reactivado correctamente.")
        return redirect('listar_inmuebles_inactivos')
    
    return render(request, 'inmueble/confirmar_activacion.html', {
        'inmueble': inmueble
    })

from .forms import CambioEstadoForm

def cambiar_estado_inmueble(request, id):
    inmueble = get_object_or_404(Inmueble, pk=id)
    reservas = SolicitudReserva.objects.filter(inmueble=inmueble).exclude(estado='cancelada')
    fechas_ocupadas = []
    for r in reservas:
        inicio = r.fecha_inicio
        fin    = r.fecha_fin
        dias   = (fin - inicio).days
        for i in range(dias + 1):
            fechas_ocupadas.append((inicio + datetime.timedelta(days=i)).isoformat())
    
    if request.method == 'POST':
        form = CambioEstadoForm(request.POST, instance=inmueble)
        if form.is_valid():
            inmueble = form.save(commit=False)
            inmueble.save()
            messages.success(request, "El mantenimiento se cargo correctamente.")
            return redirect('listar_inmuebles')  
    else:
        form = CambioEstadoForm(instance=inmueble)
    
    return render(request, 'inmueble/cambiar_estado.html', {
        'form': form,
        'inmueble': inmueble,
        'fechas_ocupadas_json': fechas_ocupadas,
    })

from django.shortcuts import render
from django.db.models import Sum, Count, ExpressionWrapper, F, FloatField
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from reservas.models import Reserva
from .models import Inmueble 

def estadisticas_inmuebles(request):
    # Fechas por defecto (últimos 30 días)
    fecha_inicio = request.GET.get('fecha_inicio', (timezone.now() - timezone.timedelta(days=30)).strftime('%Y-%m-%d'))
    fecha_fin = request.GET.get('fecha_fin', timezone.now().strftime('%Y-%m-%d'))

    # Validar fechas
    try:
        fecha_inicio_obj = timezone.datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_obj = timezone.datetime.strptime(fecha_fin, '%Y-%m-%d').date()

        if fecha_fin_obj < fecha_inicio_obj:
            fecha_inicio_obj, fecha_fin_obj = fecha_fin_obj, fecha_inicio_obj
            fecha_inicio, fecha_fin = fecha_fin, fecha_inicio
    except:
        fecha_inicio_obj = (timezone.now() - timezone.timedelta(days=30)).date()
        fecha_fin_obj = timezone.now().date()
        fecha_inicio = fecha_inicio_obj.strftime('%Y-%m-%d')
        fecha_fin = fecha_fin_obj.strftime('%Y-%m-%d')

    # Filtrar reservas confirmadas dentro del rango
    reservas = Reserva.objects.filter(
        fecha_inicio__gte=fecha_inicio_obj,
        fecha_fin__lte=fecha_fin_obj,
        estado='confirmada'
    ).annotate(
        dias=ExpressionWrapper(
            F('fecha_fin') - F('fecha_inicio'),
            output_field=FloatField()
        ),
        precio_final=ExpressionWrapper(
            F('inmueble__precio_diario') * (
                F('fecha_fin') - F('fecha_inicio')
            ),
            output_field=FloatField()
        )
    )

    # Agrupar ingresos y reservas por provincia y tipo
    ingresos_provincia = reservas.values('inmueble__provincia').annotate(
        total=Sum('precio_final')
    )
    ingresos_tipo = reservas.values('inmueble__tipo').annotate(
        total=Sum('precio_final')
    )
    reservas_provincia = reservas.values('inmueble__provincia').annotate(
        count=Count('id')
    )
    reservas_tipo = reservas.values('inmueble__tipo').annotate(
        count=Count('id')
    )

    # Calcula los totales
    total_ingresos_provincia = sum(item['total'] or 0 for item in ingresos_provincia)
    total_ingresos_tipo = sum(item['total'] or 0 for item in ingresos_tipo)
    total_reservas_provincia = sum(item['count'] or 0 for item in reservas_provincia)
    total_reservas_tipo = sum(item['count'] or 0 for item in reservas_tipo)

    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'ingresos_provincia': list(ingresos_provincia),
        'ingresos_tipo': list(ingresos_tipo),
        'reservas_provincia': list(reservas_provincia),
        'reservas_tipo': list(reservas_tipo),
        # Agrega estos nuevos campos:
        'total_ingresos_provincia': total_ingresos_provincia,
        'total_ingresos_tipo': total_ingresos_tipo,
        'total_reservas_provincia': total_reservas_provincia,
        'total_reservas_tipo': total_reservas_tipo,
    }

    return render(request, 'inmueble/menu_estadisticas.html', context)