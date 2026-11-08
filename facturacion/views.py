from django.contrib import messages                        # Para mostrar mensajes de éxito o error
from django.db.models import ProtectedError                # Error que sale al borrar una marca con productos
from django.shortcuts import render, redirect, get_object_or_404   # render: mostrar página; redirect: ir a otra; get_object_or_404: buscar o mostrar 404

from .forms import MarcaForm                               # Nuestro formulario
from .models import Marca                                  # Nuestro modelo


# =====================================================================
# MARCAS · Vistas Basadas en Funciones (VBF)
# =====================================================================

def marca_lista(request):                                  # READ: muestra todas las marcas
    q = request.GET.get("q", "")                           # 1. Leemos el buscador: /facturacion/marcas/?q=sam (si no hay, queda "")
    marcas = Marca.objects.all()                           # 2. Pedimos todas las marcas a la base de datos

    if q:                                                  # 3. Si el usuario escribió algo en el buscador...
        marcas = marcas.filter(nombre__icontains=q)        #    ...dejamos solo las que contienen ese texto

    contexto = {                                           # 4. Datos que enviamos al template
        "titulo": "Marcas",                                #    → {{ titulo }}
        "marcas": marcas,                                  #    → {% for marca in marcas %}
        "q": q,                                            #    → para que el buscador no se borre
    }
    return render(request, "facturacion/marca_lista.html", contexto)   # 5. Mostramos la página