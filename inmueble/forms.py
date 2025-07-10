from django import forms
from .models import Inmueble, Reseña

class ReseñaForm(forms.ModelForm):
    class Meta:
        model = Reseña
        fields = ['texto', 'estrellas']
        widgets = {
            'texto': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full p-2 border rounded',
                'placeholder': 'Escribe tu reseña...'
            }),
            'estrellas': forms.Select(attrs={
                'class': 'w-full p-2 border rounded'
            }),
        }
class AltaInmueble(forms.ModelForm):
    foto = forms.ImageField(required=True, 
        error_messages={'required': 'El inmueble debe tener una foto.'},
        widget=forms.FileInput())
    
    class Meta:
        model = Inmueble
        exclude = ['fecha_inicio_inactividad', 'fecha_fin_inactividad','activo', 'estado']
        labels = { 'devolucion_7dias_o_mas': 'Devolucion mayor a 7 dias',
                  'devolucion_7_a_2dias': 'Devolucion entre 7 y 2  dias',
                  'devolucion_2_a_0dias': 'Devolucion menor a 2 dias'}

class EditarInmueble(forms.ModelForm):
    foto = forms.ImageField(required=True, 
        error_messages={'required': 'El inmueble debe tener una foto.'})
    
    class Meta:
        model = Inmueble
        exclude = ['calle','numero','ciudad','provincia','pais','tipo','titulo','fecha_inicio_inactividad','fecha_fin_inactividad','activo', 'estado']
        labels = { 'devolucion_7dias_o_mas': 'Devolucion mayor a 7 dias',
                  'devolucion_7_a_2dias': 'Devolucion entre 7 y 2  dias',
                  'devolucion_2_a_0dias': 'Devolucion menor a 2 dias'}

from datetime import date

class CambioEstadoForm(forms.ModelForm):
    class Meta:
        model = Inmueble
        fields = ['fecha_inicio_inactividad', 'fecha_fin_inactividad']
        labels = {
            'fecha_inicio_inactividad': 'Fecha inicio mantenimiento',
            'fecha_fin_inactividad': 'Fecha fin mantenimiento'
        }
        widgets = {
            'fecha_inicio_inactividad': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_inactividad':     forms.DateInput(attrs={'type': 'date'}),
        }
        help_texts = {
            'fecha_inicio_inactividad': 'Seleccione la fecha en que el inmueble deja de estar disponible.',
            'fecha_fin_inactividad':     'Seleccione la fecha en que el inmueble vuelve a estar disponible.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy_str = date.today().strftime('%Y-%m-%d')
        self.fields['fecha_inicio_inactividad'].widget.attrs.update({
            'min': hoy_str
        })
        self.fields['fecha_fin_inactividad'].widget.attrs.update({
            'min': hoy_str
        })

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('fecha_inicio_inactividad')
        fin    = cleaned.get('fecha_fin_inactividad')

        if inicio and fin and fin < inicio:
            raise forms.ValidationError(
                "La fecha de fin no puede ser anterior a la fecha de inicio."
            )

        return cleaned
