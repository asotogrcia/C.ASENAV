from django.db import models
from django.utils import timezone

class Equipo(models.Model):
    ESTADOS = [
        ('optimo', 'Óptimo'),
        ('advertencia', 'Advertencia'),
        ('critico', 'Crítico'),
        ('fuera_servicio', 'Fuera de servicio'),
    ]

    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)

    estado = models.CharField(max_length=20, choices=ESTADOS, default='optimo')
    margen_mantencion_dias = models.PositiveIntegerField(help_text="Días hasta que el equipo entra en riesgo")
    ultima_mantencion = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nombre
    

    def actualizar_estado(self):
        if not self.ultima_mantencion:
            self.estado = 'advertencia'
            return

        dias_transcurridos = (timezone.now().date() - self.ultima_mantencion).days
        margen = self.margen_mantencion_dias

        if dias_transcurridos < margen * 0.5:
            self.estado = 'optimo'
        elif dias_transcurridos < margen:
            self.estado = 'advertencia'
        elif dias_transcurridos < margen * 1.5:
            self.estado = 'critico'
        else:
            self.estado = 'fuera_servicio'