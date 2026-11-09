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


def marca_crear(request):                                  # CREATE: crear una marca nueva

    if request.method == "POST":                           # ¿El usuario presionó "Guardar"? (llegó por POST)
        form = MarcaForm(request.POST)                     # 1. Llenamos el formulario con lo que escribió
        if form.is_valid():                                # 2. ¿Los datos están bien? (obligatorios, únicos, clean_nombre)
            marca = form.save()                            # 3. Guardamos en la base de datos (save devuelve la marca)
            messages.success(request, f"Marca «{marca.nombre}» creada correctamente.")   # 4. Mensaje verde
            return redirect("facturacion:marca_lista")     # 5. Vamos a la lista. Así, si recarga, no se guarda dos veces
        # Si NO es válido, no entra al if: baja hasta el render y muestra el formulario CON errores

    else:                                                  # Si llegó por GET (solo abrió la página)...
        form = MarcaForm()                                 # ...creamos un formulario vacío

    contexto = {                                           # Datos para el template
        "titulo": "Nueva marca",                           # Título de la página
        "form": form,                                      # El formulario (vacío o con errores)
        "boton": "Guardar",                                # Texto del botón
    }
    return render(request, "facturacion/marca_form.html", contexto)


def marca_editar(request, pk):                             # UPDATE. pk llega desde la URL: /marcas/editar/3/ → pk=3
    marca = get_object_or_404(Marca, pk=pk)                # 1. Buscamos la marca. Si no existe → página 404

    if request.method == "POST":                           # 2. ¿Presionó "Actualizar"?
        form = MarcaForm(request.POST, instance=marca)     #    Datos nuevos + la marca que vamos a cambiar
        if form.is_valid():                                #    ¿Están bien?
            form.save()                                    #    Actualiza (UPDATE), no crea una nueva
            messages.success(request, f"Marca «{marca.nombre}» actualizada.")
            return redirect("facturacion:marca_lista")     #    Volvemos a la lista
    else:                                                  # 3. Llegó por GET...
        form = MarcaForm(instance=marca)                   #    ...formulario lleno con los datos actuales

    contexto = {
        "titulo": f"Editar marca: {marca.nombre}",
        "form": form,
        "boton": "Actualizar",
    }
    return render(request, "facturacion/marca_form.html", contexto)   # ¡El mismo template de crear!



def marca_eliminar(request, pk):                           # DELETE
    marca = get_object_or_404(Marca, pk=pk)                # Buscamos la marca o mostramos 404

    if request.method == "POST":                           # ¿Presionó "Sí, eliminar"?
        try:                                               # Intentamos borrar...
            nombre = marca.nombre                          # Guardamos el nombre para el mensaje
            marca.delete()                                 # DELETE en la base de datos
            messages.success(request, f"Marca «{nombre}» eliminada.")
        except ProtectedError:                             # ...si tiene productos, PROTECT no deja borrarla
            messages.error(request, f"No se puede eliminar «{marca.nombre}» porque tiene productos. Desactívala en su lugar.")
        return redirect("facturacion:marca_lista")         # En los dos casos volvemos a la lista

    # Si llegó por GET: mostramos la pregunta "¿Seguro?"
    contexto = {"titulo": "Eliminar marca", "marca": marca}
    return render(request, "facturacion/marca_eliminar.html", contexto)