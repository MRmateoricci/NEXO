from django import forms

class crearReservaForm(forms.Form):
    fecha_inicio = forms.DateField(
        label='Fecha de Inicio',
        widget=forms.TextInput(attrs={'class': 'flatpickr', 'autocomplete': 'off'}),
        error_messages={'required': 'Este campo es obligatorio', 'invalid': 'Formato de fecha inválido. Usa el formato YYYY-MM-DD.'
        }
    )
    
    fecha_fin = forms.DateField(
        label='Fecha de Fin',
        widget=forms.TextInput(attrs={'class': 'flatpickr', 'autocomplete': 'off'}),
        error_messages={'required': 'Este campo es obligatorio', 'invalid': 'Formato de fecha inválido. Usa el formato YYYY-MM-DD.'
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            self.add_error('fecha_fin', 'La fecha de fin no puede ser anterior a la fecha de inicio.')