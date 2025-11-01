from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import rol_requerido
from .forms import EquipoForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Equipo
from collections import Counter
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt


#Función para filtrar
def filtrar_equipos(query):
    return Equipo.objects.filter(
        Q(nombre__icontains=query) |
        Q(categoria__icontains=query) |
        Q(estado__icontains=query)
    ).order_by('nombre')



#VISTA DE EQUIPOS - DATA
@login_required
def equipos_dashboard(request):
    query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)

    equipos = filtrar_equipos(query)

    paginator = Paginator(equipos, 8)
    page_obj = paginator.get_page(page_number)

    # Para el gráfico
    estados = Counter(e.estado for e in equipos)
    context = {
        'page_obj': page_obj,
        'query': query,
        'optimo': estados.get('Óptimo', 0),
        'advertencia': estados.get('Advertencia', 0),
        'critico': estados.get('Critico', 0),
        'fuera_servicio': estados.get('Fuera de Servicio', 0),
    }
    return render(request, "dashboard_templates/equipos.html" , context)

#VISTA DE EQUIPOS - DETALLES
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def equipo_detalle_modal(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    return render(request, 'equipos_templates/includes/detalle_equipo_modal.html', {
        'equipo': equipo
    })

#VISTA DE EQUIPOS - TABLA
@login_required
def tabla_equipos_parcial(request):
    query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)

    equipos = filtrar_equipos(query)

    paginator = Paginator(equipos, 8)
    page_obj = paginator.get_page(page_number)

    return render(request, 'equipos_templates/includes/tabla_con_paginador.html', {
        'page_obj': page_obj,
        'query': query
    })

#VISTA DE EQUIPOS - GRAFICO
@login_required
def grafico_estados_parcial(request):
    equipos = Equipo.objects.all()
    estados = Counter(e.estado for e in equipos)
    context = {
        'optimo': estados.get('Óptimo', 0),
        'advertencia': estados.get('Advertencia', 0),
        'critico': estados.get('Critico', 0),
        'fuera_servicio': estados.get('Fuera de Servicio', 0),
    }
    return render(request, "equipos_templates/includes/grafico_estados.html", context)

#VISTAS DE CREACIÓN DE EQUIPOS - FORM
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def equipo_create_form(request):
    equipo_form = EquipoForm()
    return render(request, "equipos_templates/equipo_create_form.html", {'equipo_form': equipo_form})

@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def equipo_create_submit(request):
    if request.method == 'POST':
        equipo_form = EquipoForm(request.POST)
        if equipo_form.is_valid():
            equipo = equipo_form.save()
            return JsonResponse({'success': True, 'id': equipo.id})
        html = render_to_string("equipos_templates/equipo_create_form.html", {'equipo_form': equipo_form}, request=request)
        return JsonResponse({'success': False, 'html': html})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

#VISTA DE EDICION DE EQUIPOS - FORM

@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def equipo_edit_form(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    form = EquipoForm(instance=equipo)
    return render(request, 'equipos_templates/equipo_create_form.html', {
        'equipo_form': form
    })

@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def equipo_edit(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    if request.method == 'GET':
        data = {
            'nombre': equipo.nombre,
            'categoria': equipo.categoria,
            'descripcion': equipo.descripcion,
            'ubicacion': equipo.ubicacion,
            'estado': equipo.estado,
            'activo': equipo.activo,
            'margen_mantencion_dias': equipo.margen_mantencion_dias,
            'ultima_mantencion': equipo.ultima_mantencion,
        }
        return JsonResponse(data)

    elif request.method == 'POST':
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})

#VISTA DE ELIMINACION DE EQUIPOS
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def equipo_delete(request, pk):
    if request.method == 'POST':
        equipo = get_object_or_404(Equipo, pk=pk)
        equipo.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})