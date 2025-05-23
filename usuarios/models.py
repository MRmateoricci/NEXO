from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, apellido, dni, contraseña=None, rol='inquilino'):
        if not email:
            raise ValueError("El usuario debe tener un email")
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, apellido=apellido, dni=dni, rol=rol)
        user.set_password(contraseña)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, apellido, dni, contraseña):
        user = self.create_user(email, nombre, apellido, dni, contraseña, rol='admin')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('inquilino', 'Inquilino'), ('empleado', 'Empleado')])
    estado = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'dni']

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.email})"