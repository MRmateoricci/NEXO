from django import forms
from .models import Inmueble

class AltaInmueble(forms.ModelForm):
    class Meta:
        model = Inmueble
        exclude = ['fecha_inicio_inactividad', 'fecha_fin_inactividad']

class EditarInmueble(forms.ModelForm):
    class Meta:
        model = Inmueble
        exclude = ['fecha_inicio_inactividad', 'fecha_fin_inactividad']

from datetime import date

class CambioEstadoForm(forms.ModelForm):
    class Meta:
        model = Inmueble
        fields = ['fecha_inicio_inactividad', 'fecha_fin_inactividad']
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