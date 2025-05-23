from django import forms
from .models import Usuario
from django.contrib.auth import authenticate

class RegistroForm(forms.ModelForm):
    contraseña = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirmar_contraseña = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'dni', 'email', 'contraseña', 'confirmar_contraseña', 'rol']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("contraseña")
        confirm = cleaned_data.get("confirmar_contraseña")

        if password != confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
    
class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    contraseña = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        contraseña = cleaned_data.get('contraseña')

        if email and contraseña:
            self.user = authenticate(username=email, password=contraseña)
            if self.user is None:
                raise forms.ValidationError("Email o contraseña incorrectos.")
        return cleaned_data

    def get_user(self):
        return self.user