from django.db import models
from Mantenciones.models import Mantencion

class Reporte(models.Model):
    mantencion = models.OneToOneField(Mantencion, on_delete=models.CASCADE)
    generado_en = models.DateTimeField(auto_now_add=True)
    archivo_pdf = models.FileField(upload_to='reportes/', blank=True)

    def generar_pdf(self):
        # Lógica para generar PDF desde datos de mantención
        pass

    def __str__(self):
        return f"Reporte de {self.mantencion}"
