from django.db import models
from django.utils import timezone

class Equipo(models.Model):
    ESTADOS = [
        ('Óptimo', 'Óptimo'),
        ('Advertencia', 'Advertencia'),
        ('Crítico', 'Crítico'),
        ('Fuera de Servicio', 'Fuera de Servicio'),
    ]

    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)

    estado = models.CharField(max_length=20, choices=ESTADOS, default='Óptimo')
    margen_mantencion_dias = models.PositiveIntegerField(help_text="Días hasta que el equipo entra en riesgo")
    ultima_mantencion = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        self.actualizar_estado()
        super().save(*args, **kwargs)

    def actualizar_estado(self):
        # Si no hay una fecha de última mantención, el estado es advertencia
        if not self.ultima_mantencion:
            self.estado = 'Advertencia'
            return

        # Calcular los días transcurridos desde la última mantención
        dias_transcurridos = (timezone.now().date() - self.ultima_mantencion).days
        margen = self.margen_mantencion_dias

        # Si los días transcurridos son menores a la mitad del margen, el estado es óptimo
        if dias_transcurridos < margen * 0.5:
            self.estado = 'Óptimo'
        # Si los días transcurridos son menores al margen, el estado es advertencia
        elif dias_transcurridos < margen:
            self.estado = 'Advertencia'
        # Si los días transcurridos son menores a 1.5 veces el margen, el estado es crítico
        elif dias_transcurridos < margen * 1.5:
            self.estado = 'Critico'
        # En cualquier otro caso, el estado es fuera de servicio
        else:
            self.estado = 'Fuera de Servicio'
