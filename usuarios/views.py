from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, views as auth_views
from django.contrib import messages
from .forms import RegistroForm, LoginForm, EditarUsuarioForm

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
            return redirect('login')
        else:
            messages.error(request, "Error en el registro. Por favor, corrige los errores.")
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")

    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_active:
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, "Email o contraseña incorrectos")
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def editar_usuario(request):
    usuario = request.user
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('home')
        else:
            messages.error(request, "Error al actualizar el perfil. Por favor, corrige los errores.")
    else:
        form = EditarUsuarioForm(instance=request.user)
    return render(request, 'usuarios/editar_usuario.html', {'form': form})

def home(request):
    return render(request, 'usuarios/home.html')

# View para pedir email para resetear contraseña
class PasswordReset(auth_views.PasswordResetView):
    template_name = 'usuarios/password_reset_form.html'
    # email_template_name = 'usuarios/password_reset_email.html'
    success_url = '/usuarios/password_reset/done/'

# View confirmación email enviado
class PasswordResetDone(auth_views.PasswordResetDoneView):
    template_name = 'usuarios/password_reset_done.html'

# View para poner la nueva contraseña
class PasswordResetConfirm(auth_views.PasswordResetConfirmView):
    template_name = 'usuarios/password_reset_confirm.html'
    success_url = '/usuarios/reset/done/'

# View confirmación cambio hecho
class PasswordResetComplete(auth_views.PasswordResetCompleteView):
    template_name = 'usuarios/password_reset_complete.html'