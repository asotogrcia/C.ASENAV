from django.urls import path
from . import views

app_name = 'equipos'

urlpatterns = [

    path('dashboard_equipos/', views.equipos_dashboard, name='equipos_dashboard'),

    #Crear Equipo - Formulario
    path('equipo_create_form/', views.equipo_create_form, name='formulario'),
    path('equipo_create_submit/', views.equipo_create_submit, name='crear'),



    #path('listado/', views.EquipoListView.as_view(), name='listado'),
    #path('detalle/<pk>/', views.EquipoDetailView.as_view(), name='detalle'),
    #path('crear/', views.EquipoCreateView.as_view(), name='crear'),
    #path('editar/<pk>/', views.EquipoUpdateView.as_view(), name='editar'),
    #path('eliminar/<pk>/', views.EquipoDeleteView.as_view(), name='eliminar'),
]
