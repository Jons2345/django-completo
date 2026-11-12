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
    # ---------- PRODUCTOS (Unidad 3) ----------
    path("productos/", views.producto_lista, name="producto_lista"),   # /facturacion/productos/    path("productos/crear/", views.ProductoCreateView.as_view(), name="producto_crear"),
    path("productos/crear/", views.producto_crear, name="producto_crear"),   # /facturacion/productos/crear/
    path("productos/editar/<int:pk>/", views.producto_editar, name="producto_editar"),
    path("productos/<int:pk>/", views.producto_detalle, name="producto_detalle"),   # /facturacion/productos/7/
    path("productos/eliminar/<int:pk>/", views.producto_eliminar, name="producto_eliminar"),
    
    # ---------- CATEGORÍAS (Unidad 5 · Tarea 1) ----------
        path("categorias/", views.categoria_lista, name="categoria_lista"),
        path("categorias/crear/", views.categoria_crear, name="categoria_crear"),
        path("categorias/editar/<int:pk>/", views.categoria_editar, name="categoria_editar"),
        path("categorias/eliminar/<int:pk>/", views.categoria_eliminar, name="categoria_eliminar"),
    
        # ---------- CLIENTES (Unidad 5 · Tarea 2) ----------
        path("clientes/", views.cliente_lista, name="cliente_lista"),
        path("clientes/crear/", views.cliente_crear, name="cliente_crear"),
        path("clientes/editar/<int:pk>/", views.cliente_editar, name="cliente_editar"),
        path("clientes/<int:pk>/", views.cliente_detalle, name="cliente_detalle"),
        path("clientes/eliminar/<int:pk>/", views.cliente_eliminar, name="cliente_eliminar"),
    
        # ---------- MI PERFIL (Unidad 5 · Reto) · sin <int:pk> ----------
        path("mi-perfil/", views.mi_perfil, name="mi_perfil"),
    
]