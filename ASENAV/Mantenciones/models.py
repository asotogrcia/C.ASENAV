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
    encargado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha_programada = models.DateField()
    intervalo_dias = models.PositiveIntegerField(help_text="Días hasta la próxima mantención")
    descripcion_general = models.TextField()
    correos_notificacion = models.TextField(help_text="Separar correos por coma")
    realizada = models.BooleanField(default=False)
    descripcion_realizada = models.TextField(blank=True)
    archivos = models.FileField(upload_to='mantenciones/', blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    mantencion_anterior = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    repuestos = models.ManyToManyField(Repuesto, through='RepuestoMantencion')

    def __str__(self):
        return f"Mantención de {self.equipo.nombre} - {self.fecha_programada}"

    # Devuelve la fecha de la próxima mantención
    def siguiente_fecha(self):
        # Se devuelve la fecha de la próxima mantención sumando el intervalo de días
        return self.fecha_programada + timedelta(days=self.intervalo_dias)


    # Actualiza el estado de la mantención según la fecha actual
    def actualizar_estado(self):
        # Se obtiene la fecha actual
        hoy = timezone.now().date()

        # Se verifica si la mantención ya se realizó
        if self.realizada:
            # Si se realizó, se mantiene el estado como "realizada"
            self.estado = 'realizada'
        # Se verifica si la fecha actual es posterior a la fecha programada
        elif hoy > self.fecha_programada:
            # Si la fecha actual es posterior, se mantiene el estado como "atrasada"
            self.estado = 'atrasada'
        # Se verifica si la fecha actual es igual a la fecha programada
        elif hoy == self.fecha_programada:
            # Si la fecha actual es igual, se mantiene el estado como "en_curso"
            self.estado = 'en_curso'
        else:
            # Si la fecha actual es anterior, se mantiene el estado como "pendiente"
            self.estado = 'pendiente'

        # Se guarda el estado actualizado
        self.save()


    # Finaliza una mantención y crea una nueva automáticamente
    def finalizar_mantencion(self, descripcion_final):
        # Se marca la mantención como realizada
        self.realizada = True
        # Se guarda la descripción de la mantención realizada
        self.descripcion_realizada = descripcion_final
        # Se mantiene el estado como "realizada"
        self.estado = 'realizada'
        # Se guarda la mantención actualizada
        self.save()

        # Se actualiza la última fecha de mantención del equipo
        self.equipo.ultima_mantencion = timezone.now().date()
        # Se guarda el equipo actualizado
        self.equipo.save()

        # Se crea una nueva mantención automáticamente
        nueva_fecha = timezone.now().date() + timedelta(days=self.intervalo_dias)
        # Se crea una nueva instancia de Mantención con los datos actuales
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
