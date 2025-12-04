import json
from datetime import timedelta, datetime
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from weasyprint import HTML

from django.core.mail import EmailMessage
from django.conf import settings

# Decoradores y Modelos
from core.decorators import rol_requerido
from Mantenciones.models import RepuestoMantencion
from Repuestos.models import Repuesto
from Usuarios.models import Usuario
from .models import Mantencion, ArchivoMantencion
from .forms import MantencionForm

# ==============================================================================
# 1. VISTAS DE VISUALIZACIÓN (DASHBOARD Y TABLA)
# ==============================================================================

@login_required
def dashboard_mantenciones(request):
    # 1. Consulta Principal
    mantenciones = Mantencion.objects.select_related('equipo', 'encargado').order_by('-fecha_programada')

    # 2. Paginación
    page_number = request.GET.get('page', 1)
    paginator = Paginator(mantenciones, 10)
    page_obj = paginator.get_page(page_number)

    # 3. Estadísticas
    realizadas = Mantencion.objects.filter(estado='Realizada').count()
    atrasadas = Mantencion.objects.filter(estado='Atrasada').count()
    en_curso = Mantencion.objects.filter(estado='En curso').count()
    pendientes = Mantencion.objects.filter(estado='Pendiente').count()

    # 4. DATOS PARA LOS MODALES (Vital para que funcionen los Selects)
    posibles_encargados = Usuario.objects.filter(
        rol__in=['administrador', 'supervisor', 'tecnico'], is_active=True
    )
    lista_repuestos = Repuesto.objects.filter(activo=True)

    return render(request, 'mantenciones_templates/mantenciones.html', {
        'page_obj': page_obj, # Variable estandarizada
        'q': '',
        
        # Estadísticas
        'realizadas': realizadas,
        'atrasadas': atrasadas,
        'en_curso': en_curso,
        'pendientes': pendientes,

        # Contexto para modales
        'encargados': posibles_encargados,
        'repuestos': lista_repuestos
    })


@login_required
def mantenciones_tabla(request):
    q = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)

    mantenciones = Mantencion.objects.select_related('equipo', 'encargado').all()

    if q:
        mantenciones = mantenciones.filter(
            Q(equipo__nombre__icontains=q) |
            Q(encargado__first_name__icontains=q) | 
            Q(encargado__last_name__icontains=q) |
            Q(descripcion_general__icontains=q)
        )

    mantenciones = mantenciones.order_by('-fecha_programada')
    
    paginator = Paginator(mantenciones, 10)
    page_obj = paginator.get_page(page_number)

    # DATOS PARA LOS MODALES DE EDICIÓN (Dentro de la tabla)
    posibles_encargados = Usuario.objects.filter(
        rol__in=['administrador', 'supervisor', 'tecnico'], is_active=True
    )
    lista_repuestos = Repuesto.objects.filter(activo=True)

    context = {
        'page_obj': page_obj,
        'q': q,
        'encargados': posibles_encargados,
        'repuestos': lista_repuestos
    }

    # Renderizado AJAX vs Normal
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'mantenciones_templates/includes/tabla_mantenciones.html', context)

    return render(request, 'mantenciones_templates/mantenciones.html', context)


# ==============================================================================
# 2. VISTAS DE CREACIÓN Y EDICIÓN (CRUD)
# ==============================================================================

@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def mantencion_create_form(request):
    form = MantencionForm()
    
    # 1. Filtramos los usuarios que pueden ser encargados
    posibles_encargados = Usuario.objects.filter(
        rol__in=['administrador', 'supervisor', 'tecnico'], 
        is_active=True
    ).order_by('first_name')

    return render(request, 'mantenciones_templates/includes/form_mantencion.html', {
        'form': form,
        'encargados': posibles_encargados # <--- Enviamos la lista al HTML
    })


@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def mantencion_create(request):
    if request.method == 'POST':
        form = MantencionForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Guardar Mantención
                    mantencion = form.save()
                    mantencion.actualizar_estado()

                    # 2. Crear siguiente mantención automática
                    siguiente_fecha = mantencion.fecha_programada + timedelta(days=mantencion.intervalo_dias)
                    Mantencion.objects.create(
                        equipo=mantencion.equipo,
                        encargado=mantencion.encargado,
                        fecha_programada=siguiente_fecha,
                        intervalo_dias=mantencion.intervalo_dias,
                        descripcion_general=f"Automática por Mantención ID {mantencion.id}",
                        correos_notificacion=mantencion.correos_notificacion,
                        estado='Pendiente',
                        mantencion_anterior=mantencion
                    )

                    # 3. Guardar Archivos
                    archivos = request.FILES.getlist('archivos[]')
                    
                    if len(archivos) > 3:
                        return JsonResponse({ 'success': False, 'errors': {'archivos': ['Máximo 3 archivos permitidos.']}})
                    
                    extensiones_validas = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.xlsm', '.jpg', '.png']
                    for archivo in archivos:
                        if not any(archivo.name.lower().endswith(ext) for ext in extensiones_validas):
                            return JsonResponse({'success': False, 'errors': {'archivos': [f'Archivo no permitido: {archivo.name}']}})
                    
                    for archivo in archivos:
                        ArchivoMantencion.objects.create(mantencion=mantencion, archivo=archivo)

                    # ======================================================
                    # 4. ENVÍO DE CORREO HTML (MEJORADO)
                    # ======================================================
                    
                    destinatarios = set()

                    # A. Agregar correos manuales
                    if mantencion.correos_notificacion:
                        manuales = [c.strip() for c in mantencion.correos_notificacion.split(',') if c.strip()]
                        destinatarios.update(manuales)

                    # B. Agregar correo del Encargado
                    if mantencion.encargado and mantencion.encargado.email:
                        destinatarios.add(mantencion.encargado.email)

                    lista_final = list(destinatarios)
                    
                    if lista_final:
                        asunto = f"Nueva Mantención: {mantencion.equipo.nombre}"
                        
                        # 1. RENDERIZAR EL HTML CON LOS DATOS
                        html_message = render_to_string('mantenciones_templates/email/nueva_mantencion.html', {
                            'mantencion': mantencion
                        })
                        
                        # 2. Crear versión texto plano (fallback para correos antiguos)
                        plain_message = strip_tags(html_message)

                        # 3. Configurar el remitente
                        remitente_mantencion = "ASENAV - CMMS <asenav.proyecto@gmail.com>"

                        email = EmailMessage(
                            subject=asunto,
                            body=html_message, # Usamos el HTML como cuerpo
                            from_email=remitente_mantencion,
                            to=lista_final
                        )
                        
                        # 3. ESPECIFICAR QUE ES HTML
                        email.content_subtype = "html" 

                        # 4. Adjuntar archivos
                        for archivo in archivos:
                            archivo.seek(0) 
                            email.attach(archivo.name, archivo.read(), archivo.content_type)

                        email.send(fail_silently=True)
                    # ======================================================

                return JsonResponse({'success': True, 'message': 'Mantención creada y notificaciones enviadas.'})
            
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error interno: {str(e)}'})

        return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def mantencion_editar(request, id):
    """
    Edita solo los datos de planificación (Fecha, Encargado, Estado, Descripción).
    NO edita los repuestos (eso se movió a Finalizar).
    """
    if request.method == 'POST':
        mantencion = get_object_or_404(Mantencion, id=id)
        
        try:
            with transaction.atomic():
                # 1. CAPTURA Y CONVERSIÓN DE FECHA (La solución al error)
                fecha_str = request.POST.get('fecha_programada')
                if fecha_str:
                    # Convertimos el String 'YYYY-MM-DD' a Objeto Date
                    mantencion.fecha_programada = datetime.strptime(fecha_str, '%Y-%m-%d').date()

                # 2. CAPTURA Y CONVERSIÓN DE INTERVALO
                intervalo = request.POST.get('intervalo_dias')
                if intervalo:
                    mantencion.intervalo_dias = int(intervalo)

                # 3. OTROS CAMPOS DE TEXTO
                mantencion.descripcion_general = request.POST.get('descripcion_general')
                mantencion.estado = request.POST.get('estado')
                
                # 4. ENCARGADO (Manejo de nulos)
                encargado_id = request.POST.get('encargado')
                if encargado_id:
                    mantencion.encargado_id = encargado_id
                else:
                    mantencion.encargado = None
                
                # 5. GUARDAR (Aquí se dispara tu método save() personalizado)
                # Al ser fecha_programada un objeto date, la comparación '>' funcionará.
                mantencion.save() 

            return JsonResponse({'success': True, 'message': 'Mantención actualizada correctamente.'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al actualizar: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def mantencion_delete(request, id):
    if request.method == 'POST':
        mantencion = get_object_or_404(Mantencion, id=id)
        mantencion.delete()
        return JsonResponse({'success': True, 'message': 'Mantención eliminada.'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


# ==============================================================================
# 3. FINALIZACIÓN Y REPORTES
# ==============================================================================

@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def mantencion_finalizar(request, id):
    """
    Maneja el cierre de la mantención y el descuento de repuestos.
    """
    mantencion = get_object_or_404(Mantencion, id=id)

    # --- POST: Procesar Finalización ---
    if request.method == 'POST':
        descripcion_final = request.POST.get('descripcion_realizada', '').strip()
        repuestos_json = request.POST.get('repuestos_data')

        if not descripcion_final:
            return JsonResponse({'success': False, 'message': 'La descripción del trabajo es obligatoria.'})

        try:
            with transaction.atomic():
                # 1. Finalizar la mantención (Lógica del modelo)
                mantencion.finalizar_mantencion(descripcion_final)
                
                # 2. Procesar y Guardar Repuestos (Desde el JSON del input oculto)
                if repuestos_json:
                    datos_repuestos = json.loads(repuestos_json)
                    
                    for item in datos_repuestos:
                        rep_id = item.get('id')
                        cantidad = int(item.get('cantidad'))
                        
                        if cantidad > 0:
                            # Creamos la relación. 
                            # EL MODELO RepuestoMantencion descuenta stock automáticamente en su método save()
                            RepuestoMantencion.objects.create(
                                mantencion=mantencion,
                                repuesto_id=rep_id,
                                cantidad_usada=cantidad
                            )

            return JsonResponse({'success': True, 'message': 'Mantención finalizada y repuestos descontados.'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al finalizar: {str(e)}'})

    # --- GET: Cargar el formulario en el modal ---
    # Enviamos los repuestos disponibles para llenar el Select
    repuestos = Repuesto.objects.filter(activo=True)
    
    return render(request, 'mantenciones_templates/includes/form_finalizar.html', {
        'mantencion': mantencion,
        'repuestos': repuestos
    })


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


# Vista auxiliar (Detalle modal)
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

# Vista auxiliar para editar solo formulario (si la usas con AJAX antiguo)
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

@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def subir_archivos_mantencion(request, mantencion_id):
    # Nota: El nombre del argumento 'mantencion_id' debe coincidir con lo que pusiste en urls.py
    mantencion = get_object_or_404(Mantencion, id=mantencion_id)

    if request.method == 'POST':
        archivos = request.FILES.getlist('archivos[]')
        
        # Validación básica (opcional, igual que en create)
        if len(archivos) > 3:
            return JsonResponse({'success': False, 'message': 'Máximo 3 archivos permitidos.'})

        try:
            for archivo in archivos:
                ArchivoMantencion.objects.create(mantencion=mantencion, archivo=archivo)
            return JsonResponse({'success': True, 'message': 'Archivos subidos correctamente.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al subir: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)