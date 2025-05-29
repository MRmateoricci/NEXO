from django import forms
from .models import Inmueble

class AltaInmueble(forms.ModelForm):
    class Meta:
        model = Inmueble
        fields = '__all__' 
        exclude = []

class EditarInmueble(forms.ModelForm):
    class Meta:
        model = Inmueble
        fields = '__all__'
        exclude = []