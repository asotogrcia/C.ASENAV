from django.db import models
from Equipos.models import Equipo
from Usuarios.models import Usuario
from Repuestos.models import Repuesto
from django.utils import timezone
from datetime import timedelta


class Mantencion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En curso'),
        ('realizada', 'Realizada'),
        ('atrasada', 'Atrasada'),
    ]

    equipo = models.ForeignKey('Equipo', on_delete=models.CASCADE)
    encargado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha_programada = models.DateField()
    intervalo_dias = models.PositiveIntegerField(help_text="Días hasta la próxima mantención")
    descripcion_general = models.TextField()
    correos_notificacion = models.TextField(help_text="Separar correos por coma")
    realizada = models.BooleanField(default=False)
    descripcion_realizada = models.TextField(blank=True)
    archivos = models.FileField(upload_to='mantenciones/', blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    mantencion_anterior = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    repuestos = models.ManyToManyField('Repuesto', through='RepuestoMantencion')

    def __str__(self):
        return f"Mantención de {self.equipo.nombre} - {self.fecha_programada}"

    def siguiente_fecha(self):
        return self.fecha_programada + timedelta(days=self.intervalo_dias)

    def actualizar_estado(self):
        hoy = timezone.now().date()
        if self.realizada:
            self.estado = 'realizada'
        elif hoy > self.fecha_programada:
            self.estado = 'atrasada'
        elif hoy == self.fecha_programada:
            self.estado = 'en_curso'
        else:
            self.estado = 'pendiente'
        self.save()

    def finalizar_mantencion(self, descripcion_final):
        self.realizada = True
        self.descripcion_realizada = descripcion_final
        self.estado = 'realizada'
        self.save()

        # Actualizar última mantención del equipo
        self.equipo.ultima_mantencion = timezone.now().date()
        self.equipo.save()

        # Crear nueva mantención automáticamente
        nueva_fecha = timezone.now().date() + timedelta(days=self.intervalo_dias)
        Mantencion.objects.create(
            equipo=self.equipo,
            encargado=self.encargado,
            fecha_programada=nueva_fecha,
            intervalo_dias=self.intervalo_dias,
            descripcion_general=self.descripcion_general,
            correos_notificacion=self.correos_notificacion,
            estado='pendiente',
            mantencion_anterior=self
        )

    def enviar_notificacion(self):
        # Aquí puedes integrar lógica con send_mail o Celery
        pass



class RepuestoMantencion(models.Model):
    mantencion = models.ForeignKey(Mantencion, on_delete=models.CASCADE)
    repuesto = models.ForeignKey(Repuesto, on_delete=models.CASCADE)
    cantidad_usada = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # Descontar stock al guardar
        self.repuesto.stock_actual = max(0, self.repuesto.stock_actual - self.cantidad_usada)
        self.repuesto.save()
        super().save(*args, **kwargs)
