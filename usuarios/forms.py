from django import forms
from .models import Usuario
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'dni', 'rol', 'password1', 'password2')
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }
    
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuario o Email')

class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'dni', 'rol')
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'dni': forms.TextInput(attrs={'readonly': 'readonly'}),
            'rol': forms.Select(attrs={'readonly': 'readonly'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rol'].help_text = "El rol no se puede cambiar una vez creado el usuario."
        for field in self.fields.values():
            if field.widget.attrs.get('readonly'):
                field.widget.attrs.update({
                    'style': 'background-color: #f0f0f0; color: #666; border: 1px solid #ccc;',
                })
            