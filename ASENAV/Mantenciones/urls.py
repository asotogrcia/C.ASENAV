from django.urls import path
from . import views

app_name = 'mantenciones'

urlpatterns = [
    path('mantenciones/', views.dashboard_mantenciones, name='mantenciones_dashboard'),
    path('mantenciones/tabla/', views.mantenciones_tabla, name='mantenciones_tabla'),
    path('mantenciones/create_form/', views.mantencion_create_form, name='mantencion_create_form'),
    path('mantenciones/create/', views.mantencion_create, name='mantencion_create'),
    path('mantenciones/delete/<int:id>/', views.mantencion_delete, name='mantencion_delete'),
    path('mantenciones/<int:id>/ver/', views.mantencion_detalle, name='mantencion_detalle'),
    path('mantenciones/<int:id>/editar_form/', views.mantencion_editar_form, name='mantencion_editar_form'),
    path('mantenciones/<int:id>/editar/', views.mantencion_editar, name='mantencion_editar'),
    path('mantenciones/<int:id>/finalizar/', views.mantencion_finalizar, name='mantencion_finalizar'),
    path('mantenciones/<int:id>/reporte_pdf/', views.mantencion_reporte_pdf, name='mantencion_reporte_pdf'),
]