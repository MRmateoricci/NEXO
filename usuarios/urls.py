from django.urls import path
from . import views
from .views import PasswordReset, PasswordResetDone, PasswordResetConfirm, PasswordResetComplete, registrar_tarjeta_view



urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('verificar-2fa/', views.verificar_2fa, name='verificar_2fa'),
    path('logout/', views.logout_view, name='logout'),
    path('editar/', views.editar_usuario, name='editar_usuario'),
    path('', views.home, name='home'),
    path('password_reset/', PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDone.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('lista_usuarios/', views.listar_usuarios, name='lista_usuarios'),
    path('deshabilitar/<int:usuario_id>/', views.deshabilitar_usuario, name='deshabilitar_usuario'),
    path('habilitar/<int:usuario_id>/', views.habilitar_usuario, name='habilitar_usuario'),
    path('tarjeta/nueva/', registrar_tarjeta_view, name='registrar_tarjeta'),
    path('password_change/', views.password_change_view, name='password_change'),

]