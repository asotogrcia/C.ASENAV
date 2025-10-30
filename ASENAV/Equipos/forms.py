from django import forms
from .models import Equipo
from django.utils import timezone

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ('nombre', 'categoria', 'descripcion', 'ubicacion', 'estado', 'activo', 'margen_mantencion_dias','ultima_mantencion')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre del Equipo', 'id': 'id_nombre_equipo'})
        self.fields['categoria'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Categoría del Equipo'})
        self.fields['descripcion'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Descripción del Equipo'})
        self.fields['ubicacion'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ubicación del Equipo'})
        self.fields['estado'].widget.attrs.update({'class': 'form-control'})
        self.fields['activo'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['margen_mantencion_dias'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Fecha de la última mantención'})
        self.fields['ultima_mantencion'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Fecha de la próxima mantención'})

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Equipo.objects.filter(nombre=nombre).exists():
            raise forms.ValidationError('El nombre del equipo ya existe')
        return nombre

    def clean_ultima_mantencion(self):
        ultima_mantencion = self.cleaned_data['ultima_mantencion']
        if ultima_mantencion and ultima_mantencion < timezone.now().date():
            raise forms.ValidationError('La fecha de la próxima mantención no puede ser anterior a la fecha actual')
        return ultima_mantencion

