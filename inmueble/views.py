from django.shortcuts import render
from .models import Inmueble

def listar_inmuebles(request):
    inmuebles = Inmueble.objects.all()
    return render(request, 'inmueble/listar.html', {'inmuebles' : inmuebles})

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