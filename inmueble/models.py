from django.db import models


class Inmueble(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=50, choices=[('Casa', 'casa'), ('local', 'Local'), ('Cochera', 'cochera'), ('Departamento', 'departamento')])
    metros_cuadrados = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_huespedes = models.IntegerField(default=2)
    calle = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    ciudad = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50)
    pais = models.CharField(max_length=50)
    estado = models.CharField(max_length=50, choices=[('disponible', 'Disponible'), ('reservado', 'Reservado'), ('no disponible', 'No disponible')])
    propietario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    precio_diario = models.DecimalField(max_digits=10, decimal_places=2)
# Create your models here.
