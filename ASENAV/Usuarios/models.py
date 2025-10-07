from django.db import models
from django.contrib.auth.models import AbstractUser

#Extensión de usuario de Django para técnicos y staff

class Usuario(AbstractUser):
    rut = models.CharField(max_length = 12, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('tecnico', 'Tecnico'),
        ('usuario', 'Usuario')
    ]

    rol = models.CharField(max_length=13, choices=ROL_CHOICES, default='usuario')
    especialidad = models.CharField(max_length=100, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuarios_groups',
        blank=True
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuarios_permissions',
        blank=True
    )

    def __str__(self):
        return f"{self.username} - RUT: {self.rut}"
