from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from .models import Usuario, CodigoVerificacion
from .utils import generar_codigo, enviar_codigo_verificacion
from .forms import RegistroForm, VerificacionForm, LoginForm

def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            codigo = generar_codigo(usuario)
            enviar_codigo_verificacion(usuario, codigo)
            messages.success(request, "Se ha enviado un código de verificación a tu correo.")
            return redirect('usuarios:verificar_codigo')
    else:
        form = RegistroForm()
    return render(request, 'usuarios_templates/registro.html', {'form': form})

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
                    messages.success(request, "Tu cuenta ha sido verificada correctamente.")
                    return redirect('usuarios:login')
                else:
                    messages.error(request, "El código ha expirado.")
            except CodigoVerificacion.DoesNotExist:
                messages.error(request, "El código no es válido.")
    else:
        form = VerificacionForm()
    return render(request, 'usuarios_templates/verificar.html', {'form': form})

def login_usuario(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            if usuario.is_active:
                login(request, usuario)
                return redirect('index')
            else:
                messages.error(request, 'Tu cuenta no está verificada.')
    else:
        form = LoginForm()
    return render(request, 'usuarios_templates/login.html', {'form': form})

def logout_usuario(request):
    logout(request)
    return redirect('index')

# def registro(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']
#         rut = request.POST['rut']
#         telefono = request.POST['telefono']
#         usuario = Usuario.objects.create_user(username=username, email=email, password=password, rut=rut, telefono=telefono, is_active=False)
#         codigo = generar_codigo(usuario)
#         enviar_codigo_verificacion(usuario, codigo)
#         request.session['usuario_id'] = usuario.id
#         return redirect('verificar')
#     return render(request, 'usuarios_templates/registro.html')

# def verificar(request):
#     usuario_id = request.session.get('usuario_id')
#     usuario = Usuario.objects.get(id=usuario_id)
#     if request.method == 'POST':
#         codigo_ingresado = request.POST['codigo']
#         codigo_obj = CodigoVerificacion.objects.filter(usuario=usuario, codigo=codigo_ingresado).last()
#         if codigo_obj and not codigo_obj.expirado():
#             usuario.is_active = True
#             usuario.save()
#             login(request, usuario)
#             messages.success(request, "Cuenta verificada correctamente!")
#             return redirect('index')
#         else:
#             messages.error(request, "Código inválido o expirado")
#     return render(request, 'usuarios_templates/verificar.html')