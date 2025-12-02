from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from Repuestos.models import Repuesto
from .models import Mantencion, ArchivoMantencion, RepuestoMantencion
from .forms import MantencionForm, ArchivoMantencionForm
from django.http import HttpResponse, JsonResponse
from core.decorators import rol_requerido
from datetime import timedelta
from django.core.paginator import Paginator
from django.db.models import Q
from weasyprint import HTML
from django.template.loader import render_to_string




#DASHBOARD MANTENCIÓN
@login_required
def dashboard_mantenciones(request):
    # 1. Obtenemos TODOS los registros (quitamos el [:50])
    # Guardamos en una variable temporal 'lista_completa'
    lista_completa = Mantencion.objects.select_related('equipo', 'encargado').order_by('-fecha_programada')

    # 2. Aplicamos la Paginación (Igual que en tu otra vista)
    # Cambia el '10' por el número de filas que quieras por página
    page_number = request.GET.get('page', 1)
    paginator = Paginator(lista_completa, 10) 
    page_obj = paginator.get_page(page_number)

    # Lógica de estadísticas (se mantiene igual)
    realizadas = Mantencion.objects.filter(estado='Realizada').count()
    atrasadas = Mantencion.objects.filter(estado='Atrasada').count()
    en_curso = Mantencion.objects.filter(estado='En curso').count()
    pendientes = Mantencion.objects.filter(estado='Pendiente').count()

    return render(request, 'mantenciones_templates/mantenciones.html', {
        'realizadas': realizadas,
        'atrasadas': atrasadas,
        'en_curso': en_curso,
        'pendientes': pendientes,
        
        'page_obj': page_obj, 

        'q': '' 
    })

#TABLA MANTENCIÓN
@login_required
def mantenciones_tabla(request):
    q = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)

    # Optimizamos la consulta con select_related
    mantenciones = Mantencion.objects.select_related('equipo', 'encargado').all()

    if q:
        mantenciones = mantenciones.filter(
            # 1. Buscamos por el nombre del equipo (CORRECTO)
            Q(equipo__nombre__icontains=q) |
            
            # 2. CORRECCIÓN: Buscamos por nombre o apellido del usuario encargado
            Q(encargado__first_name__icontains=q) | 
            Q(encargado__last_name__icontains=q)
        )

    mantenciones = mantenciones.order_by('-fecha_programada')
    
    paginator = Paginator(mantenciones, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'q': q,
    }

    # LÓGICA AJAX:
    # Si la petición viene de JavaScript, devolvemos SOLO la tabla (el parcial)
    es_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    print(f"¿Es petición AJAX?: {es_ajax}") # Mira esto en tu terminal negra

    if es_ajax:
        print("Entrando a renderizar PARCIAL")
        return render(request, 'mantenciones_templates/includes/tabla_mantenciones.html', context)

    print("Entrando a renderizar PADRE COMPLETO")
    return render(request, 'mantenciones_templates/mantenciones.html', context)

#VISTA MANTENCIÓN
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def mantencion_create_form(request):
    form = MantencionForm()
    repuestos = Repuesto.objects.filter(activo=True)
    return render(request, 'mantenciones_templates/includes/form_mantencion.html', {
        'form': form,
        'repuestos': repuestos
    })

@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def mantencion_create(request):
    if request.method == 'POST':
        form = MantencionForm(request.POST)
        if form.is_valid():
            mantencion = form.save()
            mantencion.actualizar_estado()

            # Crear siguiente mantención automáticamente
            siguiente_fecha = mantencion.fecha_programada + timedelta(days=mantencion.intervalo_dias)
            Mantencion.objects.create(
                equipo=mantencion.equipo,
                encargado=mantencion.encargado,
                fecha_programada=siguiente_fecha,
                intervalo_dias=mantencion.intervalo_dias,
                descripcion_general=mantencion.descripcion_general,
                correos_notificacion=mantencion.correos_notificacion,
                estado='Pendiente',
                mantencion_anterior=mantencion
            )

            # Obtener archivos enviados
            archivos = request.FILES.getlist('archivos[]')
            # Validar cantidad máxima
            if len(archivos) > 3:
                return JsonResponse({ 'success': False, 'errors': {'archivos': ['Máximo 3 archivos permitidos.']}})
            # Validar extensiones permitidas
            extensiones_validas = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.xlsm']
            for archivo in archivos:
                if not any(archivo.name.lower().endswith(ext) for ext in extensiones_validas):
                    return JsonResponse({'success': False, 'errors': {'archivos': [f'Archivo no permitido: {archivo.name}']}})
            # Guardar archivos
            for archivo in archivos:
                ArchivoMantencion.objects.create(mantencion=mantencion, archivo=archivo)

            # Guardar repuestos
            repuesto_ids = request.POST.getlist('repuesto_id[]')
            cantidades = request.POST.getlist('cantidad_usada[]')

            for repuesto_id, cantidad in zip(repuesto_ids, cantidades):
                if repuesto_id and cantidad:
                    RepuestoMantencion.objects.create(
                        mantencion=mantencion,
                        repuesto_id=repuesto_id,
                        cantidad_usada=int(cantidad)
                    )

            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})


#ELIMINACION MANTENCIÓN
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def mantencion_delete(request, id):
    mantencion = get_object_or_404(Mantencion, id=id)
    mantencion.delete()
    return JsonResponse({'success': True})


#MANTENCIÓN DETALLE
@login_required
def mantencion_detalle(request, id):
    mantencion = get_object_or_404(Mantencion, id=id)
    repuestos_usados = RepuestoMantencion.objects.filter(mantencion=mantencion)
    archivos = mantencion.archivos_adjuntos.all()

    return render(request, 'mantenciones_templates/includes/detalle_mantencion_modal.html', {
        'mantencion': mantencion,
        'repuestos_usados': repuestos_usados,
        'archivos': archivos
    })

#EDITAR MANTENCIÓN FORM
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def mantencion_editar_form(request, id):
    mantencion = get_object_or_404(Mantencion, id=id)
    form = MantencionForm(instance=mantencion)
    repuestos = Repuesto.objects.filter(activo=True)
    return render(request, 'mantenciones_templates/includes/form_mantencion.html', {
        'form': form,
        'mantencion': mantencion,
        'repuestos': repuestos
    })

#EDITAR MANTENCIÓN
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def mantencion_editar(request, id):
    mantencion = get_object_or_404(Mantencion, id=id)
    form = MantencionForm(request.POST, instance=mantencion)
    if form.is_valid():
        mantencion = form.save()
        mantencion.actualizar_estado()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})


#MANTENCIÓN REALIZADA
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def mantencion_finalizar(request, id):
    mantencion = get_object_or_404(Mantencion, id=id)

    if request.method == 'POST':
        descripcion_final = request.POST.get('descripcion_realizada', '').strip()
        if not descripcion_final:
            return JsonResponse({'success': False, 'errors': {'descripcion_realizada': ['Este campo es obligatorio.']}})
        
        mantencion.finalizar_mantencion(descripcion_final)
        return JsonResponse({'success': True})

    return render(request, 'mantenciones_templates/includes/form_finalizar.html', {
        'mantencion': mantencion
    })


#REPORTE PDF
@login_required
def mantencion_reporte_pdf(request, id):
    mantencion = get_object_or_404(Mantencion, id=id)
    if not mantencion.realizada or not mantencion.descripcion_realizada:
        return HttpResponse("La mantención aún no ha sido finalizada. No se puede generar el reporte.", status=400)


    repuestos_usados = RepuestoMantencion.objects.filter(mantencion=mantencion)
    archivos = mantencion.archivos_adjuntos.all()

    html_string = render_to_string('mantenciones_templates/reporte_pdf.html', {
        'mantencion': mantencion,
        'repuestos_usados': repuestos_usados,
        'archivos': archivos
    })

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="mantencion_{mantencion.id}.pdf"'
    return response

#VISTA ARCHIVOS MANTENCIÓN
@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def subir_archivos_mantencion(request, mantencion_id):
    mantencion = get_object_or_404(Mantencion, id=mantencion_id)

    if request.method == 'POST':
        archivos = request.FILES.getlist('archivos[]')
        for archivo in archivos:
            ArchivoMantencion.objects.create(mantencion=mantencion, archivo=archivo)
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

