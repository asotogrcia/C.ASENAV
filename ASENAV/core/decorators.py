from django.http import HttpResponseForbidden

def rol_requerido(*roles_permitidos):
    def decorador(view_func):
        def _wrapped_view(request, *args, **kwargs):
            usuario = request.user
            if not usuario.is_authenticated:
                return HttpResponseForbidden("Acceso denegado: usuario no autenticado.")
            if hasattr(usuario, 'rol') and usuario.rol in roles_permitidos:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Acceso denegado: rol insuficiente.")
        return _wrapped_view
    return decorador