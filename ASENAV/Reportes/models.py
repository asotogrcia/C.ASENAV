from django.db import models
from Usuarios.models import Usuario

class Reporte(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.titulo