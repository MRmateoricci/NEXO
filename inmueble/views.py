from django.shortcuts import render
from .models import Inmueble

def listar_inmuebles(request):
    inmuebles = Inmueble.objects.all()
    return render(request, 'inmueble/listar.html', {'inmuebles' : inmuebles})

#HU ver disponibilidad de inmueble
import json
from django.core.serializers.json import DjangoJSONEncoder

def disponibilidad_inmueble(request, id):
    inmueble = get_object_or_404(Inmueble, id=id)

    # Simulamos fechas ocupadas (ideal: traerlas desde Reservas o lo que uses)
    fechas_ocupadas = ['2025-06-10', '2025-06-15', '2025-06-20']

    eventos = [
        {
            'title': 'Ocupado',
            'start': fecha,
            'allDay': True,
            'color': 'red'
        } for fecha in fechas_ocupadas
    ]

    eventos_json = json.dumps(eventos, cls=DjangoJSONEncoder)

    return render(request, 'inmueble/disponibilidad.html', {
        'inmueble': inmueble,
        'eventos_json': eventos_json
    })

