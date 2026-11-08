from django.urls import path               # path() une una dirección con una vista
from . import views                        # Las vistas de ESTA app (facturacion/views.py)

app_name = "facturacion"                   # "Apellido" de las URLs de esta app. En templates: 'facturacion:marca_lista'

urlpatterns = [
    path("marcas/", views.marca_lista, name="marca_lista"),   # /facturacion/marcas/ → vista marca_lista
    # En los pasos siguientes agregarás aquí crear, editar y eliminar
]