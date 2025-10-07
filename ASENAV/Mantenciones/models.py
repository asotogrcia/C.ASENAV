from django.db import models
from Equipos.models import Equipo
from Usuarios.models import Usuario
from Repuestos.models import Repuesto


class Mantencion(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='mantenciones')
    tecnico = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'rol': 'tecnico'},
        related_name="mantenciones"
    )
    fecha_programada = models.DateTimeField()
    fecha_realizada = models.DateTimeField(null=True, blank=True)
    descripcion_trabajo = models.TextField(blank=True)

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    repuestos = models.ManyToManyField(Repuesto, through="RegistroUsoRepuesto", related_name="mantenciones")

    def __str__(self):
        return f"Mantención {self.id} - {self.equipo.nombre}"


class RegistroUsoRepuesto(models.Model):
    mantencion = models.ForeignKey(Mantencion, on_delete=models.CASCADE)
    repuesto = models.ForeignKey(Repuesto, on_delete=models.CASCADE)
    cantidad_usada = models.PositiveIntegerField(default=1)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cantidad_usada} x {self.componente.nombre} en Mantención {self.mantencion.id}"
