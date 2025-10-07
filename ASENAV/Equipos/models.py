from django.db import models

class Equipo(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    tipo = models.CharField(max_length=50, null=False, blank=False)
    ubicacion = models.CharField(max_length=100, null=False, blank=False)
    
    ESTADO_CHOICES = [
        ('operativo', 'Operativo'),
        ('en_reparacion', 'En Reparación'),
        ('fuera_servicio', 'Fuera de Servicio'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='operativo')
    
    def __str__(self):
        return f"{self.nombre} ({self.tipo})"
