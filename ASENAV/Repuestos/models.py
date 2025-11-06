from django.db import models

class Repuesto(models.Model):
    nombre = models.CharField("Nombre", max_length=100)
    descripcion = models.TextField("Descripción", max_length=300, blank=True, null=True)
    cantidad_stock = models.PositiveIntegerField("Cantidad en Stock", default=0)
    stock_minimo = models.PositiveIntegerField("Stock Mínimo", default=0)
    stock_maximo = models.PositiveIntegerField("Stock Máximo", default=0)
    ubicacion = models.CharField("Ubicación", max_length=100, blank=True, null=True)
    fecha_ingreso = models.DateField("Fecha de Ingreso", auto_now_add=True)
    activo = models.BooleanField("¿Activo?", default=True)

    def __str__(self):
        return f"{self.nombre} - Stock: {self.cantidad_stock}"



class MovimientoRepuesto(models.Model):
    TIPO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('egreso', 'Egreso'),
        ('ajuste', 'Ajuste'),
    ]

    repuesto = models.ForeignKey('Repuesto', on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField("Tipo de Movimiento", max_length=10, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField("Cantidad")
    fecha = models.DateTimeField("Fecha", auto_now_add=True)
    observacion = models.TextField("Observación", blank=True, null=True)

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.cantidad} - {self.repuesto.nombre}"
