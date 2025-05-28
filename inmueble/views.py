from django.shortcuts import render
from .models import Inmueble
from django.db.models import Q
from django.core.paginator import Paginator

def listar_inmuebles(request):
    # Parámetros GET (con valores por defecto y sanitización)
    tipo = request.GET.get('tipo', '').strip()
    huespedes = request.GET.get('huespedes', '').strip()
    metros = request.GET.get('metros', '').strip()

    # Filtrado
    filters = Q()
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
from datetime import timedelta
import json
from .models import Inmueble
from reservas.models import Reserva # Importar el modelo Reserved

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