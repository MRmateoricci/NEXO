from django.urls import path
from . import views

urlpatterns = [
    path('listar/', views.listar_inmuebles, name="listar_inmuebles"),
    path('<int:inmueble_id>/disponibilidad/', views.ver_disponibilidad, name='ver_disponibilidad'),
    path('ver_detalle/<int:inmueble_id>/', views.ver_detalle_inmueble, name='ver_detalle_inmueble'),
    path('alta/', views.dar_alta_inmueble, name="alta_inmueble"),
    path('eliminar/<int:id>/', views.eliminar_inmueble, name='eliminar_inmueble'),
    path('editar/<int:id>', views.editar_inmueble, name='editar_inmueble'),
    path('inmuebles/inactivos/', views.listar_inmuebles_inactivos, name='listar_inmuebles_inactivos'),
    path('inmueble/activar/<int:id>/', views.activar_inmueble, name='activar_inmueble'),
    path('inmueble/<int:id>/cambiar-estado/', views.cambiar_estado_inmueble, name='cambiar_estado_inmueble'
    ),
    path('inmueble/menu_estadisticas/', views.estadisticas_inmuebles, name='estadisticas'),
]   