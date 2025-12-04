# core/middleware.py
import os
import datetime
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings

class LicenseCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Nombre del archivo oculto que guardará la última fecha válida
        self.timestamp_file = os.path.join(settings.BASE_DIR, '.system_cache')

    def __call__(self, request):
        hoy = timezone.now().date()
        
        # Rutas exentas
        rutas_permitidas = ['/licencia-expirada/', '/static/', '/media/']
        if any(request.path.startswith(ruta) for ruta in rutas_permitidas):
            return self.get_response(request)

        # 1. BLOQUEO POR FECHA LÍMITE (Vencimiento normal)
        if hoy > settings.LICENSE_EXPIRATION_DATE:
            return render(request, 'licencia_expirada.html', status=403)

        # 2. BLOQUEO POR MANIPULACIÓN DE FECHA (Anti-Cheat)
        last_seen_date = self.get_last_seen_date()

        if last_seen_date and hoy < last_seen_date:
            # Si la fecha de 'hoy' es MENOR a la última vez que se usó,
            # significa que retrasaron el reloj de Windows.
            return render(request, 'licencia_expirada.html', {
                'mensaje_extra': 'Error de integridad temporal detectado. Por favor ajuste la fecha del sistema correctamente.'
            }, status=403)

        # Si todo está bien, actualizamos la "última vez visto" a hoy
        self.update_last_seen_date(hoy)

        return self.get_response(request)

    def get_last_seen_date(self):
        """Lee la fecha guardada en el archivo oculto"""
        if not os.path.exists(self.timestamp_file):
            return None
        try:
            with open(self.timestamp_file, 'r') as f:
                date_str = f.read().strip()
                return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return None

    def update_last_seen_date(self, hoy):
        """Guarda la fecha de hoy si es mayor a la guardada"""
        last_date = self.get_last_seen_date()
        # Solo actualizamos si hoy es posterior a lo que ya tenemos
        if not last_date or hoy > last_date:
            with open(self.timestamp_file, 'w') as f:
                f.write(hoy.strftime("%Y-%m-%d"))