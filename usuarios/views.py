from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, views as auth_views
from django.contrib import messages

from reservas.models import TarjetaPago
from .forms import RegistroForm, LoginForm, EditarUsuarioForm, Codigo2FAForm
from .models import Usuario
from inmueble.models import Inmueble
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django import forms
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone


def registro(request):
    if request.user.is_authenticated:
        if request.user.rol == 'admin':
            # Admin puede registrar con cualquier rol
            if request.method == 'POST':
                form = RegistroForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Usuario registrado exitosamente.")
                    return redirect('home')
                else:
                    messages.error(request, "Error en el registro. Verifique los datos ingresados.")
                    exit
            else:
                form = RegistroForm()

        elif request.user.rol == 'empleado':
            # Empleado solo puede registrar inquilinos
            if request.method == 'POST':
                form = RegistroForm(request.POST)
                if form.is_valid():
                    usuario = form.save(commit=False)
                    usuario.rol = 'inquilino'  # forzar rol
                    usuario.save()
                    messages.success(request, "Usuario inquilino registrado exitosamente.")
                    return redirect('home')
                else:
                    messages.error(request, "Error en el registro. Verifique los datos ingresados.")
                    form.fields['rol'].widget = forms.HiddenInput()
            else:
                form = RegistroForm()
                form.fields['rol'].initial = 'inquilino'
                form.fields['rol'].widget = forms.HiddenInput()
        else:
            # Usuario autenticado sin permisos
            messages.error(request, "No tienes permiso para registrar nuevos usuarios.")
            return redirect('home')

    else:
        # Usuario no autenticado: solo se puede registrar como inquilino
        if request.method == 'POST':
            form = RegistroForm(request.POST)
            if form.is_valid():
                usuario = form.save(commit=False)
                usuario.rol = 'inquilino'
                usuario.save()
                messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
                return redirect('login')
            else:
                messages.error(request, "Error en el registro. Verifique los datos ingresados.")
                form.fields['rol'].widget = forms.HiddenInput()
        else:
            form = RegistroForm()
            form.fields['rol'].initial = 'inquilino'
            form.fields['rol'].widget = forms.HiddenInput()

    return render(request, 'usuarios/registro.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.rol == 'admin':
                codigo = get_random_string(length=6, allowed_chars='0123456789')
                print(f"Código de verificación 2FA: {codigo}")  # Para pruebas, eliminar en producción
                request.session['codigo_2fa'] = codigo
                request.session['usuario_2fa_id'] = user.id
                request.session['codigo_2fa_time'] = timezone.now().timestamp()

                send_mail(
                    'Código de verificación 2FA',
                    f'Tu código es: {codigo}',
                    'no-reply@tusitio.com',
                    [user.email],
                )
                return redirect('verificar_2fa')

            login(request, user)
            messages.success(request, f"Bienvenido, {user.first_name}.")
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})

def verificar_2fa(request):
    if 'usuario_2fa_id' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        form = Codigo2FAForm(request.POST)
        if form.is_valid():
            codigo_ingresado = form.cleaned_data['codigo']
            codigo_guardado = request.session.get('codigo_2fa')
            codigo_time = request.session.get('codigo_2fa_time')
            tiempo_actual = timezone.now().timestamp()
            if not codigo_ingresado == codigo_guardado:
                messages.error(request, "Código incorrecto.")
            if codigo_time:
                if tiempo_actual - codigo_time > 60:
                    messages.error(request, "El código ha expirado. Por favor, vuelve a iniciar sesión.")
                    # Limpia la sesión 
                    request.session.pop('codigo_2fa', None)
                    request.session.pop('usuario_2fa_id', None)
                    request.session.pop('codigo_2fa_time', None)
                    return redirect('login')

            if codigo_ingresado == codigo_guardado:
                user_id = request.session.get('usuario_2fa_id')
                user = Usuario.objects.get(id=user_id)
                login(request, user)

                request.session.pop('codigo_2fa', None)
                request.session.pop('usuario_2fa_id', None)

                return redirect('home')
    else:
        form = Codigo2FAForm()

    return render(request, 'usuarios/verificar_2fa.html', {'form': form})

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
    inmuebles = Inmueble.objects.all()  # Obtener todos los inmuebles
    return render(request, 'usuarios/home.html' , {'inmuebles': inmuebles})

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

@login_required
def listar_usuarios(request):
    if request.user.rol not in ['admin', 'empleado']:
        return redirect('home')
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})

@login_required
def deshabilitar_usuario(request, usuario_id):
    if request.user.rol not in  ['admin', 'empleado']:
        return redirect('home')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    usuario.is_active = False
    usuario.save()
    messages.success(request, f'Usuario {usuario.email} deshabilitado correctamente.')
    return redirect('lista_usuarios')

@login_required
def habilitar_usuario(request, usuario_id):
    if request.user.rol not in ['admin', 'empleado']:
        return redirect('home')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    usuario.is_active = True
    usuario.save()
    messages.success(request, f'Usuario {usuario.email} habilitado correctamente.')
    return redirect('lista_usuarios')

@login_required
def registrar_tarjeta_view(request):
    if request.method == 'POST':
        numero = request.POST.get('numero')
        vencimiento = request.POST.get('vencimiento')
        cvv = request.POST.get('cvv')

        if not (numero and vencimiento and cvv):
            return render(request, 'usuarios/registrar_tarjeta.html', {'error': 'Completá todos los campos.'})

        if TarjetaPago.objects.filter(numero=numero, titular=request.user).exists():
            return render(request, 'usuarios/registrar_tarjeta.html', {'error': 'Ya registraste esta tarjeta.'})

        TarjetaPago.objects.create(
            titular=request.user,
            numero=numero,
            vencimiento=vencimiento,
            cvv=cvv
        )

        return render(request, 'usuarios/tarjeta_registrada.html')

    return render(request, 'usuarios/registrar_tarjeta.html')