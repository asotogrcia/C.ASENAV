from django.db import models
from Equipos.models import Equipo
from Usuarios.models import Usuario
from Repuestos.models import Repuesto
from django.utils import timezone
from datetime import timedelta


class Mantencion(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('En curso', 'En curso'),
        ('Realizada', 'Realizada'),
        ('Atrasada', 'Atrasada'),
    ]

    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    encargado = models.ForeignKey( Usuario, on_delete=models.SET_NULL, null=True)
    fecha_programada = models.DateField()
    fecha_realizada = models.DateField(blank=True, null=True)
    intervalo_dias = models.PositiveIntegerField( help_text="Días hasta la próxima mantención")
    descripcion_general = models.TextField()
    correos_notificacion = models.TextField( help_text="Separar correos por coma")
    realizada = models.BooleanField(default=False)
    descripcion_realizada = models.TextField(blank=True)
    archivos = models.FileField(upload_to='mantenciones/', blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    mantencion_anterior = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    repuestos = models.ManyToManyField(Repuesto, through='RepuestoMantencion')

    def __str__(self):
        return f"Mantención de {self.equipo.nombre} - {self.fecha_programada}"
    

    # Actualiza el estado de la mantención
    def save(self, *args, **kwargs):
        self._actualizando_estado = True
        self.actualizar_estado()
        self._actualizando_estado = False
        super().save(*args, **kwargs)

    # Devuelve la fecha de la próxima mantención
    def siguiente_fecha(self):
        # Se devuelve la fecha de la próxima mantención sumando el intervalo de días
        return self.fecha_programada + timedelta(days=self.intervalo_dias)

    # Actualiza el estado de la mantención según la fecha actual
    def actualizar_estado(self):
        hoy = timezone.now().date()

        if self.realizada:
            self.estado = 'Realizada'
        elif hoy > self.fecha_programada:
            self.estado = 'Atrasada'
        elif hoy == self.fecha_programada:
            self.estado = 'En curso'
        else:
            self.estado = 'Pendiente'

        # Solo guardar si no estamos dentro de save()
        if not getattr(self, '_actualizando_estado', False):
            self.save()

    # Finaliza una mantención y crea una nueva automáticamente
    def finalizar_mantencion(self, descripcion_final):
        self.realizada = True
        self.descripcion_realizada = descripcion_final
        self.fecha_realizada = timezone.now().date()
        self.estado = 'Realizada'
        self.save()

        self.equipo.ultima_mantencion = self.fecha_realizada
        self.equipo.save()


    def enviar_notificacion(self):
        # Aquí puedes integrar lógica con send_mail o Celery
        pass


class RepuestoMantencion(models.Model):
    mantencion = models.ForeignKey(Mantencion, on_delete=models.CASCADE)
    repuesto = models.ForeignKey(Repuesto, on_delete=models.CASCADE)
    cantidad_usada = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # Descontar stock al guardar
        self.repuesto.cantidad_stock = max( 0, self.repuesto.cantidad_stock - self.cantidad_usada)
        self.repuesto.save()
        super().save(*args, **kwargs)


class ArchivoMantencion(models.Model):
    mantencion = models.ForeignKey(Mantencion, on_delete=models.CASCADE, related_name='archivos_adjuntos')
    archivo = models.FileField(upload_to='mantenciones/')
    descripcion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.archivo.name