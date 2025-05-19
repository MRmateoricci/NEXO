from django.db import models

class Reserva(models.Model):
    inquilino = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    inmueble = models.ForeignKey('inmueble.Inmueble', on_delete=models.CASCADE)
    fecha_reserva = models.DateField(default=models.DateField(auto_now_add=True))
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=50, choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')])

class SolicitudReserva(models.Model):
    inquilino = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    inmueble = models.ForeignKey('inmueble.Inmueble', on_delete=models.CASCADE)
    fecha_solicitud = models.DateField(default=models.DateField(auto_now_add=True))
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=50, choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')])

# Create your models here.
