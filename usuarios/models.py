from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('inquilino', 'Inquilino'),
        ('empleado', 'Empleado'),
    )
    dni = models.CharField(max_length=8, unique=True, verbose_name='DNI')
    rol = models.CharField(max_length=20, choices=ROLES, default='Inquilino')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.dni})"