from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import rol_requerido
from .forms import EquipoForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Equipo

@login_required
def equipos_dashboard(request):
    equipos = Equipo.objects.all()
    context = {
        'equipos': equipos,
    }
    return render(request, "dashboard_templates/equipos.html" , context)


@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def equipo_create_form(request):
    equipo_form = EquipoForm()
    return render(request, "equipos_templates/equipo_create_form.html", {'equipo_form': equipo_form})

@login_required
@rol_requerido('administrador', 'supervisor', 'tecnico')
def equipo_create_submit(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            equipo = form.save()
            return JsonResponse({'success': True, 'id': equipo.id})
        html = render_to_string("equipos_templates/equipo_create_form.html", {'form': form}, request=request)
        return JsonResponse({'success': False, 'html': html})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})