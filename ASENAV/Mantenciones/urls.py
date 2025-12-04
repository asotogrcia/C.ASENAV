from django.urls import path
from . import views

app_name = 'mantenciones'

urlpatterns = [
    # Dashboard y Tabla
    path('mantenciones/', views.dashboard_mantenciones, name='mantenciones_dashboard'),
    path('mantenciones/tabla/', views.mantenciones_tabla, name='mantenciones_tabla'),

    # Creación (CRUD)
    path('mantenciones/create_form/', views.mantencion_create_form, name='mantencion_create_form'),
    path('mantenciones/create/', views.mantencion_create, name='mantencion_create'),
    
    # Edición (CRUD)
    # Nota: 'editar_form' se usa si cargas el form por AJAX antiguo. 
    # 'editar' recibe el POST del modal dentro de la tabla.
    path('mantenciones/<int:id>/editar_form/', views.mantencion_editar_form, name='mantencion_editar_form'),
    path('mantenciones/<int:id>/editar/', views.mantencion_editar, name='mantencion_editar'),
    
    # Eliminación
    path('mantenciones/delete/<int:id>/', views.mantencion_delete, name='mantencion_delete'),

    # Acciones Específicas
    path('mantenciones/<int:id>/ver/', views.mantencion_detalle, name='mantencion_detalle'),
    
    # FINALIZACIÓN (Aquí está la lógica nueva de repuestos)
    path('mantenciones/<int:id>/finalizar/', views.mantencion_finalizar, name='mantencion_finalizar'),
    
    # Reportes
    path('mantenciones/<int:id>/reporte_pdf/', views.mantencion_reporte_pdf, name='mantencion_reporte_pdf'),
    
    # Archivos
    path('mantenciones/<int:mantencion_id>/subir_archivos/', views.subir_archivos_mantencion, name='subir_archivos_mantencion'),
]