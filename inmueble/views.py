from django.shortcuts import render,redirect, get_object_or_404
from .models import Inmueble
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages

def listar_inmuebles(request):
    # Parámetros GET (con valores por defecto y sanitización)
    filters = Q(activo=True)
    tipo = request.GET.get('tipo', '').strip()
    huespedes = request.GET.get('huespedes', '').strip()
    metros = request.GET.get('metros', '').strip()

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


def ver_detalle_inmueble(request, inmueble_id):
    inmueble = get_object_or_404(Inmueble, pk=inmueble_id)
    return render(request, 'inmueble/ver_detalle.html', {'inmueble': inmueble})

from .forms import AltaInmueble

def dar_alta_inmueble(request):
    if request.method == 'POST':
        formulario = AltaInmueble(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Inmueble dado de alta correctamente.")
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