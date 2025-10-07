from django.db import models

class Repuesto(models.Model):
    nombre = models.CharField(max_length=100, blank=False, null=False)
    descripcion = models.TextField(max_length=300, blank=True, null=True)
    cantidad_stock = models.PositiveIntegerField(default=0)
    ubicacion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - Stock: {self.cantidad_stock}"