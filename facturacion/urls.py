from django.contrib import admin
from django.contrib.auth import views as auth_views    # NUEVO: vistas de login y logout de Django (con apodo auth_views)
from django.urls import path, include
from . import views                                    # Nuestras vistas


app_name = "facturacion"                   # "Apellido" de las URLs de esta app. En templates: 'facturacion:marca_lista'

urlpatterns = [
    path("marcas/", views.marca_lista, name="marca_lista"),   # /facturacion/marcas/ → vista marca_lista
    # En los pasos siguientes agregarás aquí crear, editar y eliminar
    path("marcas/crear/", views.marca_crear, name="marca_crear"),   # /facturacion/marcas/crear/
    path("marcas/editar/<int:pk>/", views.marca_editar, name="marca_editar"),
    path("marcas/eliminar/<int:pk>/", views.marca_eliminar, name="marca_eliminar"),
        # ---------- PRODUCTOS: clases (Unidad 3) ----------
    path("productos/", views.ProductoListView.as_view(), name="producto_lista"),   # .as_view() es obligatorio en las clases
    path("productos/crear/", views.ProductoCreateView.as_view(), name="producto_crear"),
        # Las VBC buscan el registro por un parámetro que se llame pk
    path("productos/editar/<int:pk>/", views.ProductoUpdateView.as_view(), name="producto_editar"),
    path("productos/<int:pk>/", views.ProductoDetailView.as_view(), name="producto_detalle"),
    path("productos/eliminar/<int:pk>/", views.ProductoDeleteView.as_view(), name="producto_eliminar"),
    
]