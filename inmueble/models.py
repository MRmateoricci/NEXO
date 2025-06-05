from django.db import models


class Inmueble(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=50, choices=[('casa', 'Casa'), ('local', 'Local'), ('cochera', 'Cochera'), ('departamento', 'Departamento')])
    metros_cuadrados = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_huespedes = models.IntegerField(default=2)
    calle = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    ciudad = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50)
    pais = models.CharField(max_length=50)
    estado = models.CharField(max_length=50, choices=[('Disponible', 'Disponible'), ('Reservado', 'Reservado'), ('no disponible', 'No disponible')])
    precio_diario = models.DecimalField(max_digits=10, decimal_places=2)
# Create your models here.
    def __str__(self):
        return f"{self.titulo} - {self.tipo}"
