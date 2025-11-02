from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Repuesto, MovimientoRepuesto
from django.core.paginator import Paginator
from .forms import RepuestoForm, MovimientoRepuestoForm
from django.db import models
from django.db.models.functions import TruncMonth
from django.db.models import Count
from core.decorators import rol_requerido



#Vista Dashboard de Repuestos
@login_required
def repuestos(request):
    return render(request, 'repuestos_templates/repuestos.html')

# Vista detalle de Repuestos
@login_required
def repuesto_detalle_modal(request, pk):
    repuesto = get_object_or_404(Repuesto, pk=pk)
    return render(request, 'repuestos_templates/includes/repuesto_detalle_modal.html', {
        'repuesto': repuesto
    })

#Vista Tabla de Repuestos
@login_required
def repuestos_tabla(request):
    query = request.GET.get('q', '')
    repuestos = Repuesto.objects.filter(nombre__icontains=query)
    paginator = Paginator(repuestos, 8)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'repuestos_templates/includes/tabla_con_paginador.html', {
        'page_obj': page_obj,
        'query': query
    })

#Vista Formulario de Repuesto
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def repuesto_create_form(request):
    form = RepuestoForm()
    return render(request, 'repuestos_templates/includes/form_repuesto.html', {
        'repuesto_form': form
    })

#Vista Submit de Repuesto
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def repuesto_create(request):
    form = RepuestoForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})


#Vista Formulario de Edicion de Repuesto
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def repuesto_edit_form(request, pk):
    repuesto = get_object_or_404(Repuesto, pk=pk)
    form = RepuestoForm(instance=repuesto)
    return render(request, 'repuestos_templates/includes/form_repuesto.html', {
        'repuesto_form': form
    })

#Vista Submit de Edicion de Repuesto
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def repuesto_edit(request, pk):
    repuesto = get_object_or_404(Repuesto, pk=pk)
    form = RepuestoForm(request.POST, instance=repuesto)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})

#Vista Eliminación de Repuesto
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def repuesto_delete(request, pk):
    repuesto = get_object_or_404(Repuesto, pk=pk)
    repuesto.delete()
    return JsonResponse({'success': True})

#Vista Grafico de Stock
@login_required
def grafico_stock_estado(request):
    repuestos = Repuesto.objects.all()
    bajo = repuestos.filter(cantidad_stock__lt=models.F('stock_minimo')).count()
    dentro = repuestos.filter(cantidad_stock__gte=models.F('stock_minimo'), cantidad_stock__lte=models.F('stock_maximo')).count()
    excedido = repuestos.filter(cantidad_stock__gt=models.F('stock_maximo')).count()

    data = {
        'labels': ['Bajo', 'Óptimo', 'Excedido'],
        'values': [bajo, dentro, excedido],
        'colors': ['#dc3545', '#198754', '#ffc107']
    }
    return JsonResponse(data)

#Vista Grafico de Ubicaciones
@login_required
def grafico_ubicacion(request):
    ubicaciones = Repuesto.objects.values('ubicacion').annotate(total=Count('id')).order_by('-total')
    data = {
        'labels': [u['ubicacion'] or 'Sin ubicación' for u in ubicaciones],
        'values': [u['total'] for u in ubicaciones],
        'colors': ['#0d6efd', '#20c997', '#6f42c1', '#fd7e14', '#0dcaf0']
    }
    return JsonResponse(data)

#Vista Grafico de Estado
@login_required
def grafico_repuestos_estado(request):
    activos = Repuesto.objects.filter(activo=True).count()
    inactivos = Repuesto.objects.filter(activo=False).count()
    return JsonResponse({
        'labels': ['Activos', 'Inactivos'],
        'values': [activos, inactivos],
        'colors': ['#198754', '#dc3545']
    })

#Vista Grafico de Stock Critico
@login_required
def grafico_stock_critico(request):
    criticos = Repuesto.objects.filter(cantidad_stock__lt=models.F('stock_minimo'))
    labels = [r.nombre for r in criticos]
    values = [r.cantidad_stock for r in criticos]
    minimos = [r.stock_minimo for r in criticos]
    return JsonResponse({
        'labels': labels,
        'values': values,
        'minimos': minimos,
        'colors': ['#dc3545'] * len(labels)
    })

#Vista Grafico de Ingresos Mensuales
@login_required
def grafico_ingreso_mensual(request):
    ingresos = MovimientoRepuesto.objects.filter(tipo='ingreso') \
        .annotate(mes=TruncMonth('fecha')) \
        .values('mes') \
        .annotate(total=Count('id')) \
        .order_by('mes')

    labels = [i['mes'].strftime('%b') for i in ingresos]
    values = [i['total'] for i in ingresos]

    return JsonResponse({
        'labels': labels,
        'values': values,
        'color': '#0d6efd'
    })

#Movimiento Repuesto
#Form Movimiento de Repuesto
@login_required
def movimiento_create_form(request):
    form = MovimientoRepuestoForm()
    return render(request, 'repuestos_templates/includes/form_movimiento.html', {
        'movimiento_form': form
    })

#Crear Movimiento de Repuesto
@login_required
def movimiento_create(request):
    if request.method == 'POST':
        form = MovimientoRepuestoForm(request.POST)
        if form.is_valid():
            movimiento = form.save()
            repuesto = movimiento.repuesto
            if movimiento.tipo == 'ingreso':
                repuesto.cantidad_stock += movimiento.cantidad
            elif movimiento.tipo == 'egreso':
                repuesto.cantidad_stock = max(0, repuesto.cantidad_stock - movimiento.cantidad)
            elif movimiento.tipo == 'ajuste':
                repuesto.cantidad_stock = movimiento.cantidad
            repuesto.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})