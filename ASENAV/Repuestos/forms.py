from django import forms
from .models import Repuesto, MovimientoRepuesto

class RepuestoForm(forms.ModelForm):
    class Meta:
        model = Repuesto
        fields = [
            'nombre',
            'descripcion',
            'cantidad_stock',
            'stock_minimo',
            'stock_maximo',
            'ubicacion',
            'activo',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del repuesto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción (opcional)',
                'style': 'resize: none;'
            }),
            'cantidad_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'stock_maximo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Bodega Central, Estante 3'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_activo_switch'
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'cantidad_stock': 'Stock Actual',
            'stock_minimo': 'Stock Mínimo',
            'stock_maximo': 'Stock Máximo',
            'ubicacion': 'Ubicación',
            'activo': '¿Activo?',
        }



#Formulario para el movimiento de repuestos
class MovimientoRepuestoForm(forms.ModelForm):
    class Meta:
        model = MovimientoRepuesto
        fields = ['repuesto', 'tipo', 'cantidad', 'observacion']
        widgets = {
            'repuesto': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
