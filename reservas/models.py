from django.db import models

class Reserva(models.Model):
    inquilino = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    inmueble = models.ForeignKey('inmueble.Inmueble', on_delete=models.CASCADE)
    fecha_reserva = models.DateField(auto_now_add=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=50, choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')])

class Inquilino(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, null=True, blank=True)  # Opcional (si es usuario registrado)
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=20)
    edad = models.PositiveIntegerField()
    creado_por = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name='inquilinos_creados')  # Quién lo registró

    def __str__(self):
        return self.nombre
    
class SolicitudReserva(models.Model):
    inquilino = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    inquilinos = models.ManyToManyField(Inquilino)
    inmueble = models.ForeignKey('inmueble.Inmueble', on_delete=models.CASCADE)
    fecha_solicitud = models.DateField(auto_now_add=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=50, choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')], default='pendiente')





