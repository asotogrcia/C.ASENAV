from django.urls import path
from . import views

app_name = 'repuestos'

urlpatterns = [
    # Dashboard principal
    path('repuestos/', views.repuestos, name='repuestos'),

    # Tabla con búsqueda y paginación (AJAX)
    path('repuestos/tabla/', views.repuestos_tabla, name='repuestos_tabla'),

    # Crear repuesto
    path('repuestos/create_form/', views.repuesto_create_form, name='repuesto_create_form'),
    path('repuestos/create/', views.repuesto_create, name='repuesto_create'),

    # Crear movimiento de repuesto
    path('repuestos/movimiento/create_form/', views.movimiento_create_form, name='movimiento_create_form'),
    path('repuestos/movimiento/create/', views.movimiento_create, name='movimiento_create'),

    # Editar repuesto
    path('repuestos/<int:pk>/edit_form/', views.repuesto_edit_form, name='repuesto_edit_form'),
    path('repuestos/<int:pk>/edit/', views.repuesto_edit, name='repuesto_edit'),

    # Eliminar repuesto
    path('repuestos/<int:pk>/delete/', views.repuesto_delete, name='repuesto_delete'),

    # Detalle en modal
    path('repuestos/<int:pk>/detalle_modal/', views.repuesto_detalle_modal, name='repuesto_detalle_modal'),

    # Gráficos
    path('repuestos/grafico_stock_estado/', views.grafico_stock_estado, name='grafico_stock_estado'),
    path('repuestos/grafico_ubicacion/', views.grafico_ubicacion, name='grafico_ubicacion'),
    path('repuestos/grafico_estado/', views.grafico_repuestos_estado, name='grafico_repuestos_estado'),
    path('repuestos/grafico_stock_critico/', views.grafico_stock_critico, name='grafico_stock_critico'),
    path('repuestos/grafico_ingreso_mensual/', views.grafico_ingreso_mensual, name='grafico_ingreso_mensual'),

]