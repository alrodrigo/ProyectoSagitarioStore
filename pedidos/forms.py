from django import forms
from .models import DireccionEnvio, Pedido, MetodoEnvio

class DireccionEnvioForm(forms.ModelForm):
    """Formulario para crear o editar una dirección de envío"""
    class Meta:
        model = DireccionEnvio
        fields = [
            'nombre_completo', 
            'direccion', 
            'ciudad', 
            'departamento', 
            'codigo_postal', 
            'telefono', 
            'es_predeterminada'
        ]
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre completo'}),
            'direccion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Dirección completa'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ciudad'}),
            'departamento': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Departamento'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Código postal (opcional)'}),
            'telefono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Número de teléfono'}),
        }

class MetodoEnvioForm(forms.Form):
    """Formulario para seleccionar un método de envío"""
    metodo_envio = forms.ModelChoiceField(
        queryset=MetodoEnvio.objects.filter(activo=True),
        widget=forms.RadioSelect,
        empty_label=None
    )

class MetodoPagoForm(forms.Form):
    """Formulario para seleccionar el método de pago"""
    METODO_PAGO_CHOICES = Pedido.METODO_PAGO_CHOICES
    
    metodo_pago = forms.ChoiceField(
        choices=METODO_PAGO_CHOICES,
        widget=forms.RadioSelect,
    )
    
    referencia_pago = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input', 
            'placeholder': 'Número de comprobante o referencia (opcional)'
        })
    )
    
class NotasForm(forms.Form):
    """Formulario para agregar notas adicionales al pedido"""
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea', 
            'placeholder': 'Instrucciones especiales o notas para el pedido (opcional)',
            'rows': 3
        })
    )