from django.urls import path               # path() une una dirección con una vista
from . import views                        # Las vistas de ESTA app (facturacion/views.py)

app_name = "facturacion"                   # "Apellido" de las URLs de esta app. En templates: 'facturacion:marca_lista'

urlpatterns = [
    path("marcas/", views.marca_lista, name="marca_lista"),   # /facturacion/marcas/ → vista marca_lista
    # En los pasos siguientes agregarás aquí crear, editar y eliminar
    path("marcas/crear/", views.marca_crear, name="marca_crear"),   # /facturacion/marcas/crear/
    path("marcas/editar/<int:pk>/", views.marca_editar, name="marca_editar"),
    path("marcas/eliminar/<int:pk>/", views.marca_eliminar, name="marca_eliminar"),
]