from django.shortcuts import render
from Usuarios.forms import RegistroForm, LoginForm, VerificacionForm
from django.contrib.auth.decorators import login_required

def index(request):
    registro_form = RegistroForm()
    login_form = LoginForm()
    verificacion_form = VerificacionForm()
    return render(request, "index.html", {
        'registro_form' : registro_form,
        'login_form' : login_form,
        'verificacion_form' : verificacion_form,
    })

@login_required
def dashboard(request):
    return render(request, "dashboard_templates/dashboard.html")   