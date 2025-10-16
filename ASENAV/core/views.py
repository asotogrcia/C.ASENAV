from django.shortcuts import render
from Usuarios.forms import RegistroForm, LoginForm, VerificacionForm

def index(request):
    registro_form = RegistroForm()
    login_form = LoginForm()
    return render(request, "index.html", {
        'registro_form' : registro_form,
        'login_form' : login_form,
    })