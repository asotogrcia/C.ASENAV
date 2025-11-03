from django import forms
from .models import Mantencion, ArchivoMantencion, RepuestoMantencion

#FORMULARIO MANTENCIÓN
class MantencionForm(forms.ModelForm):
    class Meta:
        model = Mantencion
        fields = [
            'equipo', 'encargado', 'fecha_programada', 'intervalo_dias',
            'descripcion_general', 'correos_notificacion'
        ]
        widgets = {
            'equipo': forms.Select(attrs={'class': 'form-select'}),
            'encargado': forms.Select(attrs={'class': 'form-select'}),
            'intervalo_dias': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'fecha_programada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion_general': forms.Textarea(attrs={'rows': 3, 'style': 'resize: none;', 'class': 'form-control'}),
            'correos_notificacion': forms.Textarea(attrs={'rows': 2, 'style': 'resize: none;', 'class': 'form-control'}),
        }

#FORMULARIO ARCHIVO MANTENCIÓN
class ArchivoMantencionForm(forms.ModelForm):
    class Meta:
        model = ArchivoMantencion
        fields = ['archivo', 'descripcion']

class RepuestoMantencionForm(forms.ModelForm):
    class Meta:
        model = RepuestoMantencion
        fields = ['repuesto', 'cantidad_usada']
