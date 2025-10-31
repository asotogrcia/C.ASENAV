from django import forms
from .models import Equipo
from django.utils import timezone

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = (
            'nombre',
            'categoria',
            'descripcion',
            'ubicacion',
            'estado',
            'activo',
            'margen_mantencion_dias',
            'ultima_mantencion'
        )
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del equipo',
                'id': 'id_nombre_equipo'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Categoría del equipo'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del equipo',
                'rows': 2,
                'style': 'resize: none;'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación del equipo'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch',
                'id': 'id_activo_switch'
            }),
            'margen_mantencion_dias': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Días hasta riesgo de mantención',
                'min': 1
            }),
            'ultima_mantencion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            },
            format='%Y-%m-%d'
            ),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        qs = Equipo.objects.filter(nombre=nombre)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError('Ya existe un equipo con este nombre.')

        return nombre

    def clean_ultima_mantencion(self):
        ultima_mantencion = self.cleaned_data.get('ultima_mantencion')
        if ultima_mantencion and ultima_mantencion > timezone.now().date():
            raise forms.ValidationError('La fecha de la ultima mantención no puede ser posterior a la fecha actual.')
        return ultima_mantencion

