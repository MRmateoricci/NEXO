from django.urls import path

from . import views


urlpatterns = [
    # URL para la vista de reservas
    path('', views.ReservasView, name='reservas'),
    path('reservar/<int:inmueble_id>/', views.crearReservaView, name='crear_reserva'),
    
    # URL para la vista de crear reserva
    #path('reservas/crear/', CrearReservaView.as_view(), name='crear_reserva'),
    
    # URL para la vista de editar reserva
    #path('reservas/editar/<int:pk>/', EditarReservaView.as_view(), name='editar_reserva'),
    
    # URL para la vista de eliminar reserva
    path('cancelar/', views.eliminarReservaView, name='cancelar_reserva'),
    path('confirmarcancelacion/<int:reserva_id>', views.confirmar_cancelacion_reserva_view, name='confirmar_cancelacion'),
    path('buscar-usuarios/', views.buscar_usuarios_view, name='buscar_usuarios'),
    path('gestion-inquilinos/<int:reserva_id>/', views.gestion_inquilinos_view, name='gestion_inquilinos'),
    path('validar/', views.validarSolicitudReservaView, name='validar_solicitud_reserva'),
    path('ver-solicitudes-pendientes/<int:inquilino_id>/', views.verSolicitudesPendientesView, name='ver_solicitudes_pendientes'),
    path('cancelar_pendiente/<int:solicitud_id>/', views.confirmar_cancelacion_pendiente, name='confirmar_cancelacion_pendiente'),
    path('reserva/pagar/<int:solicitud_id>/', views.pagar_reserva_view, name='pagar_reserva'),


]