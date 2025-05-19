from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=100)
    rol = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('Inquilino', 'Inquilino'), ('Empleado', 'Empleado')])
    estado = models.BooleanField(default=True)
# Create your models here.
