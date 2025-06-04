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
    path('eliminar/', views.eliminarReservaView, name='eliminar_reserva'),

    path('buscar-usuarios/', views.buscar_usuarios_view, name='buscar_usuarios'),
    path('gestion-inquilinos/<int:reserva_id>/', views.gestion_inquilinos_view, name='gestion_inquilinos'),
]