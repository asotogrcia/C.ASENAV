import random
from django.utils import timezone
from datetime import timedelta
from .models import CodigoVerificacion
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags


#Función para generar el código de verificación de usuario
def generar_codigo(usuario):
    codigo = str(random.randint(100000,999999))
    expiracion = timezone.now() + timedelta(minutes=10)
    CodigoVerificacion.objects.create(usuario=usuario, codigo=codigo, expiracion=expiracion)
    return codigo


#Funcion para enviar el código de verificación
def enviar_codigo_verificacion(usuario, codigo):
    asunto = "🔐 Código de Verificación - Sistema ASENAV"
    
    # 1. Renderizamos el HTML pasando el usuario y el código
    html_message = render_to_string('usuarios_templates/email/codigo_verificacion.html', {
        'usuario': usuario,
        'codigo': codigo
    })
    
    # 2. Creamos una versión en texto plano por si el gestor de correo no lee HTML
    plain_message = strip_tags(html_message)
    
    destinatarios = [usuario.email]

    # 3. Destinatario Personalizado
    remitente_personalizado = "ASENAV - SEGURIDAD <asenav.proyecto@gmail.com>"

    # 3. Configuramos el correo
    email = EmailMessage(
        subject=asunto,
        body=html_message, # Cuerpo HTML
        from_email=remitente_personalizado,
        to=destinatarios
    )
    
    # 4. Indicamos que el contenido es HTML
    email.content_subtype = "html" 
    
    # 5. Enviamos
    email.send(fail_silently=True)