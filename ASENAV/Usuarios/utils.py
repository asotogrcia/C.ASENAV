import random
from django.utils import timezone
from datetime import timedelta
from .models import CodigoVerificacion

from django.core.mail import send_mail
from django.conf import settings

#Función para generar el código de verificación de usuario
def generar_codigo(usuario):
    codigo = str(random.randint(100000,999999))
    expiracion = timezone.now() + timedelta(minutes=10)
    CodigoVerificacion.objects.create(usuario=usuario, codigo=codigo, expiracion=expiracion)
    return codigo


#Funcion para enviar el código de verificación
def enviar_codigo_verificacion(usuario, codigo):
    asunto = "Código de Verificación - Sistema ASENAV CMMS"
    mensaje = f"Hola {usuario.username},\n\nTu código de verificación es: {codigo}\n\nExpira en 10 minutos."
    remitente = settings.DEFAULT_FROM_EMAIL
    destinatarios = [usuario.email]
    send_mail(asunto, mensaje, remitente, destinatarios)