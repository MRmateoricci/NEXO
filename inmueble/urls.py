from django.urls import path
from . import views

urlpatterns = [
    path('listar/', views.listar_inmuebles, name="listar_inmuebles"),
    path('<int:inmueble_id>/disponibilidad/', views.ver_disponibilidad, name='ver_disponibilidad'),
    path('ver_detalle/<int:inmueble_id>/', views.ver_detalle_inmueble, name='ver_detalle_inmueble'),
]   