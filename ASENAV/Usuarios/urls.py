from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('registro/', views.registro_usuario, name='registro'),
    path('verificar/', views.verificar_codigo, name='verificar_codigo'),
    path('gestion/', views.gestion_usuarios, name='gestion_usuarios'),
    path('actualizar/<int:user_id>/', views.actualizar_usuario, name='actualizar_usuario'),
]
