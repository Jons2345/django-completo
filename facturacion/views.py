from django.contrib.auth.decorators import login_required   # ← NUEVO, junto a las demás importaciones
from django.contrib.auth.mixins import LoginRequiredMixin   # ← NUEVO, junto a las demás importaciones
from django.contrib import messages                        # Para mostrar mensajes de éxito o error
from django.db.models import ProtectedError                # Error que sale al borrar una marca con productos
from django.shortcuts import render, redirect, get_object_or_404   # render: mostrar página; redirect: ir a otra; get_object_or_404: buscar o mostrar 404
from django.urls import reverse_lazy                      # NUEVO: name de URL → dirección (para atributos de clase)
from django.views.generic import (                        # NUEVO: las 5 vistas genéricas de Django
    ListView, CreateView, UpdateView, DetailView, DeleteView,
)

from .forms import MarcaForm, ProductoForm                                # Nuestro formulario
from .models import Marca, Producto                                  # Nuestro modelo

# =====================================================================
# MARCAS · Vistas Basadas en Funciones (VBF)
# =====================================================================

@login_required          # ← Antes de ejecutar marca_lista revisa la sesión. Sin sesión → /login/?next=...
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

@login_required          # ← Pónselo a las 4 funciones de marcas
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

@login_required 
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


@login_required 
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




# =====================================================================
# PRODUCTOS · Vistas Basadas en Clases (VBC)
# =====================================================================

class ProductoListView(LoginRequiredMixin, ListView):                          # Heredamos de ListView: ya sabe listar registros
    # ---------- ATRIBUTOS (configuración) ----------
    model = Producto                                       # ¿Qué tabla lista? La de productos
    template_name = "facturacion/producto_lista.html"      # ¿Qué HTML usa para mostrarla?
    context_object_name = "productos"                      # Nombre de la lista en el HTML: {% for producto in productos %}
    paginate_by = 5                                        # Muestra 5 por página y envía page_obj al template

    # ---------- MÉTODOS (cambiamos dos pasos) ----------
    def get_queryset(self):                                # Paso que decide QUÉ productos se muestran
        q = self.request.GET.get("q", "")                  # Leemos el buscador. En una clase, request está en self.request
        productos = Producto.objects.all()                 # Empezamos con todos los productos
        if q:                                              # Si el usuario escribió algo...
            productos = productos.filter(nombre__icontains=q)   # ...dejamos solo los que contienen ese texto
        return productos                                   # Devolvemos la lista: ListView la pagina y la manda al HTML

    def get_context_data(self, **kwargs):                  # Paso que arma los datos que recibe el HTML
        contexto = super().get_context_data(**kwargs)      # 1. Pedimos a ListView lo que ya preparó (productos, page_obj)
        contexto["titulo"] = "Productos"                   # 2. Agregamos el título → {{ titulo }}
        contexto["q"] = self.request.GET.get("q", "")      # 3. Agregamos lo buscado → para que no se borre del buscador
        return contexto                                    # 4. Entregamos todo junto
    


class ProductoCreateView(LoginRequiredMixin, CreateView):                      # Heredamos de CreateView: ya sabe mostrar y guardar un formulario
    model = Producto                                       # ¿Qué tabla? Productos
    form_class = ProductoForm                              # ¿Qué formulario? El de forms.py
    template_name = "facturacion/producto_form.html"       # ¿Qué HTML muestra el formulario?
    success_url = reverse_lazy("facturacion:producto_lista")   # ¿A dónde ir después de guardar? A la lista

    # Lo que hace CreateView sola (no lo escribes):
    #   GET  → crea form_class vacío y dibuja template_name
    #   POST → llena el form con request.POST y revisa form.is_valid()
    #            válido   → llama a form_valid()   → guarda → va a success_url
    #            inválido → llama a form_invalid() → vuelve a dibujar el form con errores

    def get_context_data(self, **kwargs):                  # Datos extra para el HTML
        contexto = super().get_context_data(**kwargs)      # Lo que CreateView ya preparó (incluye "form")
        contexto["titulo"] = "Nuevo producto"              # → {{ titulo }}
        contexto["boton"] = "Guardar"                      # → {{ boton }}
        return contexto

    def form_valid(self, form):                            # Se ejecuta SOLO si el formulario está bien
        messages.success(self.request, f"Producto «{form.instance.nombre}» creado.")   # form.instance = el producto
        return super().form_valid(form)                    # La versión original: guarda (también las categorías N:M) y redirige
    

class ProductoUpdateView(LoginRequiredMixin, UpdateView):                      # Heredamos de UpdateView: ya sabe editar un registro
    model = Producto                                       # ¿Qué tabla?
    form_class = ProductoForm                              # El mismo formulario de crear
    template_name = "facturacion/producto_form.html"       # ¡El mismo template de crear!
    success_url = reverse_lazy("facturacion:producto_lista")   # A dónde ir al terminar

    # Lo que hace UpdateView sola:
    #   toma el <int:pk> de la URL, busca ese producto y lo guarda en self.object
    #   GET  → formulario LLENO con los datos de self.object
    #   POST → revisa y actualiza ese mismo producto (no crea uno nuevo)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)      # Incluye "form" y "object"
        contexto["titulo"] = f"Editar producto: {self.object.nombre}"   # self.object = el producto que editamos
        contexto["boton"] = "Actualizar"
        return contexto

    def form_valid(self, form):                            # Si los datos están bien...
        messages.success(self.request, f"Producto «{form.instance.nombre}» actualizado.")   # ...mensaje verde
        return super().form_valid(form)                    # ...y la versión original guarda y redirige

    def form_invalid(self, form):                          # Si los datos tienen errores...
        messages.error(self.request, "Revisa los campos marcados en rojo.")   # ...mensaje rojo arriba
        return super().form_invalid(form)                  # ...y la versión original vuelve a mostrar el form
    

class ProductoDetailView(LoginRequiredMixin, DetailView):                      # Heredamos de DetailView: muestra UN registro
    model = Producto                                       # ¿Qué tabla?
    template_name = "facturacion/producto_detalle.html"    # ¿Qué HTML?
    context_object_name = "producto"                       # En el HTML: {{ producto.nombre }}
    # No necesita métodos: busca el producto por el pk de la URL y lo envía al template
    


class ProductoDeleteView(LoginRequiredMixin, DeleteView):                      # Heredamos de DeleteView: pregunta y elimina
    model = Producto                                       # ¿Qué tabla?
    template_name = "facturacion/producto_eliminar.html"   # HTML con la pregunta "¿Seguro?"
    context_object_name = "producto"                       # En el HTML: {{ producto.nombre }}
    success_url = reverse_lazy("facturacion:producto_lista")   # A dónde ir después de eliminar

    # Lo que hace DeleteView sola:
    #   GET  → busca el producto por pk y muestra la pregunta
    #   POST → elimina el producto y va a success_url

    def form_valid(self, form):                            # Se ejecuta al confirmar (POST)
        messages.success(self.request, f"Producto «{self.object.nombre}» eliminado.")   # self.object = el que se elimina
        return super().form_valid(form)                    # La versión original hace el delete() y redirige
    
