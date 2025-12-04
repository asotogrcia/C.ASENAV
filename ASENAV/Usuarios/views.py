from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CodigoVerificacion
from .utils import generar_codigo, enviar_codigo_verificacion
from .forms import RegistroForm, VerificacionForm, LoginForm
from django.contrib.auth.decorators import login_required
from core.decorators import rol_requerido
from .models import Usuario

def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            codigo = generar_codigo(usuario)
            enviar_codigo_verificacion(usuario, codigo)
            return JsonResponse({
                'success': True,
                'message': "Se ha enviado un código de verificación a tu correo."
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def verificar_codigo(request):
    if request.method == 'POST':
        form = VerificacionForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            try:
                verificacion = CodigoVerificacion.objects.get(codigo=codigo)
                if not verificacion.expirado():
                    usuario = verificacion.usuario
                    usuario.is_active = True
                    usuario.save()
                    verificacion.delete()
                    return JsonResponse({'success': True, 'message': 'Cuenta verificada correctamente. Ya puedes iniciar sesión.'})
                else:
                    return JsonResponse({'success': False, 'message': 'El código ha expirado.'})
            except CodigoVerificacion.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'El código no es válido.'})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def login_usuario(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            if usuario.is_active:
                login(request, usuario)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Tu cuenta está inactiva o no está verificada.'})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def logout_usuario(request):
    logout(request)
    return redirect('index')

#Panel de Administración de Usuarios
@login_required
@rol_requerido('administrador')
def gestion_usuarios(request):
    q = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)

    # 1. Base de la consulta (excluyendo superusuarios de Django si quieres)
    usuarios_list = Usuario.objects.filter(is_superuser=False).order_by('first_name', 'last_name')

    # 2. Búsqueda inteligente (incluye RUT y especialidad)
    if q:
        usuarios_list = usuarios_list.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(rut__icontains=q) |          # Buscamos por RUT
            Q(especialidad__icontains=q)   # Buscamos por especialidad
        )

    # 3. Paginación (Usamos 10 usuarios por página)
    paginator = Paginator(usuarios_list, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'q': q
    }

    # 4. Lógica AJAX (Igual que en mantenciones)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'usuarios_templates/includes/tabla_usuarios.html', context)

    return render(request, 'usuarios_templates/usuarios.html', context)


@login_required
@rol_requerido('administrador')
def actualizar_usuario(request, user_id):
    if request.method == 'POST':
        # Usamos get_object_or_404, pero si falla, Ajax recibirá un 404 que podemos manejar
        usuario = get_object_or_404(Usuario, id=user_id)
        
        try:
            # --- BLOQUE DE SEGURIDAD (ANTI-SUICIDIO) ---
            if usuario.id == request.user.id:
                nuevo_estado_activo = request.POST.get('is_active') == 'on'
                nuevo_rol = request.POST.get('rol')

                if not nuevo_estado_activo:
                    # RESPUESTA JSON DE ERROR
                    return JsonResponse({
                        'success': False, 
                        'message': '¡Acción denegada! No puedes desactivar tu propia cuenta.'
                    })

                if nuevo_rol != 'administrador':
                    # RESPUESTA JSON DE ERROR
                    return JsonResponse({
                        'success': False, 
                        'message': '¡Acción denegada! No puedes quitarte el rol de administrador.'
                    })
            # -------------------------------------------

            # Actualización de datos
            usuario.first_name = request.POST.get('first_name')
            usuario.last_name = request.POST.get('last_name')
            usuario.email = request.POST.get('email')
            usuario.rut = request.POST.get('rut')
            usuario.telefono = request.POST.get('telefono')
            
            usuario.rol = request.POST.get('rol')
            usuario.especialidad = request.POST.get('especialidad')
            usuario.is_active = request.POST.get('is_active') == 'on'

            usuario.save()
            
            # RESPUESTA JSON DE ÉXITO
            return JsonResponse({
                'success': True, 
                'message': f'Usuario {usuario.username} actualizado correctamente.'
            })
            
        except Exception as e:
            # Captura de errores inesperados (ej: RUT duplicado)
            return JsonResponse({
                'success': False, 
                'message': f'Error al actualizar: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)