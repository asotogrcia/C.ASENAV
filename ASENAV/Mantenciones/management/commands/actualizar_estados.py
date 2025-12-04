from django.core.management.base import BaseCommand
from django.utils import timezone
from Mantenciones.models import Mantencion

class Command(BaseCommand):
    help = 'Actualiza automáticamente el estado de las mantenciones según la fecha actual'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando actualización diaria de estados...")
        
        # 1. Filtramos solo las que NO están realizadas para ahorrar recursos
        mantenciones_activas = Mantencion.objects.exclude(estado='Realizada')
        
        contador = 0
        for m in mantenciones_activas:
            estado_anterior = m.estado
            
            # Llamamos a tu método existente en el modelo
            # Nota: Asegúrate de que tu método save() no tenga lógica que rompa el script
            # Si tu método save() ya llama a actualizar_estado(), basta con m.save()
            m.actualizar_estado() 
            
            # Solo guardamos si hubo cambio (opcional, pero optimiza)
            if m.estado != estado_anterior:
                m.save()
                contador += 1
                self.stdout.write(f"Mantención {m.id} ({m.equipo.nombre}): {estado_anterior} -> {m.estado}")

        self.stdout.write(self.style.SUCCESS(f'Proceso finalizado. {contador} mantenciones actualizadas.'))