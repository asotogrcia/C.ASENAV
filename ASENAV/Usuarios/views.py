from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import JsonResponse
from .models import CodigoVerificacion
from .utils import generar_codigo, enviar_codigo_verificacion
from .forms import RegistroForm, VerificacionForm, LoginForm

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
                return JsonResponse({'success': False, 'message': 'Tu cuenta no está verificada.'})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def logout_usuario(request):
    logout(request)
    return redirect('index')