from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User

ESTRELLAS_CHOICES = [
    (1, '★☆☆☆☆'),
    (2, '★★☆☆☆'),
    (3, '★★★☆☆'),
    (4, '★★★★☆'),
    (5, '★★★★★'),
]

class Inmueble(models.Model):
    titulo = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=50, choices=[('Casa', 'Casa'), ('Local', 'Local'), ('Cochera', 'Cochera'), ('Departamento', 'Departamento')])
    metros_cuadrados = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_huespedes = models.IntegerField(default=2)
    banos = models.IntegerField(default=2)
    calle = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    ciudad = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50)
    pais = models.CharField(max_length=50)
    estado = models.CharField(max_length=50, choices=[('Disponible', 'Disponible'), ('Reservado', 'Reservado'), ('No disponible', 'No disponible')])
    activo = models.BooleanField(default=True)
    precio_diario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio_inactividad = models.DateField(null=True,blank=True,)
    fecha_fin_inactividad = models.DateField(null=True,blank=True,)
    minimo_dias_reserva = models.IntegerField(default=1)
    maximo_dias_reserva = models.IntegerField(default=30)
    devolucion_7dias_o_mas = models.IntegerField(default=0,null=False,blank=False)
    devolucion_7_a_2dias = models.IntegerField(default=0,null=False,blank=False)
    devolucion_2_a_0dias = models.IntegerField(default=0,null=False,blank=False)
    
    foto = models.ImageField(
        upload_to='inmuebles/',
        null=True,
        blank=True
    )
    estrellas = models.IntegerField(choices=ESTRELLAS_CHOICES, default=3)
    def promedio_calificacion(self):
        promedio = self.calificaciones.aggregate(Avg('puntaje'))['puntaje__avg']
        return round(promedio, 1) if promedio else 0
    
# Create your models here.
    def __str__(self):
        return f"{self.titulo} - {self.tipo}"
    
from django.conf import settings

class Calificacion(models.Model):
    inmueble = models.ForeignKey(Inmueble, related_name='calificaciones', on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puntaje = models.PositiveSmallIntegerField(choices=[(1, '1 estrella'), (2, '2 estrellas'), (3, '3 estrellas'),
                                                         (4, '4 estrellas'), (5, '5 estrellas')])
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('inmueble', 'usuario')  # Para que un usuario no califique dos veces el mismo inmueble

    def __str__(self):
        return f"{self.usuario} → {self.inmueble}: {self.puntaje} estrellas"

class Reseña(models.Model):
    inmueble = models.ForeignKey('Inmueble', on_delete=models.CASCADE, related_name='resenas')
    inquilino = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    estrellas = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('inmueble', 'inquilino')  # Un inquilino puede dejar solo 1 reseña por inmueble

    def __str__(self):
        return f"{self.inquilino.username} - {self.estrellas}⭐"