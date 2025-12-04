from django.shortcuts import render
from Usuarios.forms import RegistroForm, LoginForm, VerificacionForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from Equipos.models import Equipo
from Mantenciones.models import Mantencion
import json

def index(request):
    registro_form = RegistroForm()
    login_form = LoginForm()
    verificacion_form = VerificacionForm()
    return render(request, "index.html", {
        'registro_form' : registro_form,
        'login_form' : login_form,
        'verificacion_form' : verificacion_form,
    })

@login_required
def dashboard(request):
    # ==========================================
    # 1. DATOS PARA GRÁFICOS (CHART.JS)
    # ==========================================
    
    # A. Estado Equipos
    equipos_data = Equipo.objects.values('estado').annotate(total=Count('id'))
    labels_equipos = [item['estado'] for item in equipos_data]
    data_equipos = [item['total'] for item in equipos_data]

    # B. Estado Mantenciones
    mant_estado_data = Mantencion.objects.values('estado').annotate(total=Count('id'))
    labels_mant = [item['estado'] for item in mant_estado_data]
    data_mant = [item['total'] for item in mant_estado_data]

    # C. Top Equipos Intervenidos
    top_equipos = Mantencion.objects.values('equipo__nombre').annotate(total=Count('id')).order_by('-total')[:5]
    labels_top = [item['equipo__nombre'] for item in top_equipos]
    data_top = [item['total'] for item in top_equipos]

    # D. Evolución Mensual
    por_mes = Mantencion.objects.annotate(mes=TruncMonth('fecha_programada')).values('mes').annotate(total=Count('id')).order_by('mes')
    labels_mes = [item['mes'].strftime('%b') for item in por_mes] # Ene, Feb...
    data_mes = [item['total'] for item in por_mes]

    # ==========================================
    # 2. DATOS PARA CALENDARIO (FULLCALENDAR)
    # ==========================================
    
    consulta_mantenciones = Mantencion.objects.select_related('equipo', 'encargado').all()
    eventos_calendario = []

    for m in consulta_mantenciones:
        # Colores visuales para el calendario
        color = '#ffc107' # Amarillo (Pendiente)
        if m.estado == 'Realizada': color = '#198754' # Verde
        elif m.estado == 'Atrasada': color = '#dc3545' # Rojo
        elif m.estado == 'En curso': color = '#0d6efd' # Azul

        encargado_nombre = f"{m.encargado.first_name} {m.encargado.last_name}" if m.encargado else "Sin asignar"

        eventos_calendario.append({
            'title': m.equipo.nombre,
            'start': m.fecha_programada.isoformat(), # YYYY-MM-DD
            'backgroundColor': color,
            'borderColor': color,
            # Props extendidas para el Modal Acordeón
            'extendedProps': {
                'id': m.id,
                'estado': m.estado,
                'encargado': encargado_nombre,
                'descripcion': m.descripcion_general,
                'color': color
            }
        })

    # ==========================================
    # 3. CONTADORES (TARJETAS)
    # ==========================================
    stats = {
        'realizadas': Mantencion.objects.filter(estado='Realizada').count(),
        'atrasadas': Mantencion.objects.filter(estado='Atrasada').count(),
        'en_curso': Mantencion.objects.filter(estado='En curso').count(),
        'pendientes': Mantencion.objects.filter(estado='Pendiente').count(),
    }

    context = {
        **stats,
        # JSON Dumps para JS
        'labels_equipos': json.dumps(labels_equipos),
        'data_equipos': json.dumps(data_equipos),
        'labels_mant': json.dumps(labels_mant),
        'data_mant': json.dumps(data_mant),
        'labels_top': json.dumps(labels_top),
        'data_top': json.dumps(data_top),
        'labels_mes': json.dumps(labels_mes),
        'data_mes': json.dumps(data_mes),
        'calendar_events': json.dumps(eventos_calendario),
    }

    return render(request, "dashboard_templates/dashboard.html", context)