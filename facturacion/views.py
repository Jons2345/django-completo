from django.contrib.auth.decorators import login_required   # ← NUEVO, junto a las demás importaciones
from django.core.paginator import Paginator                # NUEVO: corta una lista en páginas
from django.contrib import messages                        # Para mostrar mensajes de éxito o error
from django.db.models import ProtectedError, Q                # Error que sale al borrar una marca con productos
from django.shortcuts import render, redirect, get_object_or_404   # render: mostrar página; redirect: ir a otra; get_object_or_404: buscar o mostrar 404

from .forms import MarcaForm, ProductoForm, CategoriaForm, ClienteForm, PerfilForm   # Nuestros formularios
from .models import Marca, Producto, Categoria, Cliente, Perfil                      # Nuestros modelos# Nuestro modelo

# =====================================================================
# MARCAS · Vistas Basadas en Funciones (VBF)
# =====================================================================

@login_required          # ← Antes de ejecutar marca_lista revisa la sesión. Sin sesión → /login/?next=...
def marca_lista(request):                                  # READ: muestra todas las marcas
    q = request.GET.get("q", "")                           # Buscador: ?q=sam
    marcas = Marca.objects.all()
    if q:
        marcas = marcas.filter(nombre__icontains=q)
    contexto = {"titulo": "Marcas", "marcas": marcas, "q": q}
    return render(request, "facturacion/marca_lista.html", contexto)


@login_required          # ← Pónselo a las 4 funciones de marcas
def marca_crear(request):                                  # CREATE
    if request.method == "POST":                           # POST: guardar
        form = MarcaForm(request.POST)
        if form.is_valid():
            marca = form.save()
            messages.success(request, f"Marca «{marca.nombre}» creada correctamente.")
            return redirect("facturacion:marca_lista")
    else:                                                  # GET: formulario vacío
        form = MarcaForm()
    contexto = {"titulo": "Nueva marca", "form": form, "boton": "Guardar"}
    return render(request, "facturacion/marca_form.html", contexto)


@login_required 
def marca_editar(request, pk):                             # UPDATE
    marca = get_object_or_404(Marca, pk=pk)
    if request.method == "POST":
        form = MarcaForm(request.POST, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, f"Marca «{marca.nombre}» actualizada.")
            return redirect("facturacion:marca_lista")
    else:
        form = MarcaForm(instance=marca)
    contexto = {"titulo": f"Editar marca: {marca.nombre}", "form": form, "boton": "Actualizar"}
    return render(request, "facturacion/marca_form.html", contexto)


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
# PRODUCTOS · Vistas Basadas en Funciones (VBF)
# =====================================================================
@login_required
def producto_lista(request):                               # READ: lista de productos con buscador y páginas
    q = request.GET.get("q", "")                           # 1. Texto del buscador: /productos/?q=laptop (si no hay, "")

    productos = (                                          # 2. Pedimos los productos a la base de datos
        Producto.objects
        .select_related("marca")                           #    1:N → trae la marca en la MISMA consulta (JOIN)
        .prefetch_related("categorias")                    #    N:M → trae todas las categorías en UNA consulta extra
    )                                                      #    Sin estas 2 líneas la tabla haría 2 consultas POR CADA producto

    if q:                                                  # 3. Si escribió algo en el buscador...
        productos = productos.filter(nombre__icontains=q)  #    ...dejamos solo los que contienen ese texto

    paginador = Paginator(productos, 5)                    # 4. Corta la lista de 5 en 5
    numero = request.GET.get("page")                       # 5. ¿Qué página pidió? /productos/?page=2 (si no hay, None)
    page_obj = paginador.get_page(numero)                  # 6. Esa página. Si piden ?page=abc da la 1; si piden ?page=99, la última

    contexto = {
        "titulo": "Productos",                             # → {{ titulo }}
        "page_obj": page_obj,                              # → {% for producto in page_obj %} (solo trae los 5 de esta página)
        "q": q,                                            # → para que el buscador no se borre
    }
    return render(request, "facturacion/producto_lista.html", contexto)                              # 4. Entregamos todo junto
    
@login_required
def producto_crear(request):                               # CREATE: crear un producto nuevo

    if request.method == "POST":                           # ¿Presionó "Guardar"? (llegó por POST)
        form = ProductoForm(request.POST)                  # 1. Llenamos el formulario con lo que envió
        if form.is_valid():                                # 2. ¿Todo bien? (obligatorios, marca existe, clean_precio...)
            producto = form.save()                         # 3. INSERT del producto + INSERT de sus categorías (N:M)
            messages.success(request, f"Producto «{producto.nombre}» creado.")
            return redirect("facturacion:producto_lista")  # 4. A la lista (Post/Redirect/Get)
        # Si NO es válido, baja hasta el render y muestra el formulario CON errores

    else:                                                  # Llegó por GET (abrió la página)...
        form = ProductoForm()                              # ...formulario vacío

    contexto = {
        "titulo": "Nuevo producto",
        "form": form,                                      # Vacío (GET) o con datos y errores (POST inválido)
        "boton": "Guardar",
    }
    return render(request, "facturacion/producto_form.html", contexto)

@login_required
def producto_editar(request, pk):                          # UPDATE. pk viene de la URL: /productos/editar/7/ → pk=7
    producto = get_object_or_404(Producto, pk=pk)          # 1. Buscamos el producto. Si no existe → página 404

    if request.method == "POST":                           # 2. ¿Presionó "Actualizar"?
        form = ProductoForm(request.POST, instance=producto)   # Datos nuevos + el producto que vamos a cambiar
        if form.is_valid():
            form.save()                                    # UPDATE del producto y reemplaza sus categorías por las marcadas
            messages.success(request, f"Producto «{producto.nombre}» actualizado.")
            return redirect("facturacion:producto_lista")
        messages.error(request, "Revisa los campos marcados en rojo.")   # Solo llega aquí si NO es válido
    else:                                                  # 3. Llegó por GET...
        form = ProductoForm(instance=producto)             #    ...formulario LLENO con los datos actuales (y sus casillas marcadas)

    contexto = {
        "titulo": f"Editar producto: {producto.nombre}",
        "form": form,
        "boton": "Actualizar",
    }
    return render(request, "facturacion/producto_form.html", contexto)   # El mismo template de crear

@login_required
def producto_detalle(request, pk):                         # READ (uno): la ficha de un producto
    producto = get_object_or_404(Producto, pk=pk)          # Buscamos el producto número pk o mostramos 404
    contexto = {"producto": producto}                      # Solo necesitamos enviar el producto
    return render(request, "facturacion/producto_detalle.html", contexto)
    # Esta vista solo atiende GET: no tiene formulario, así que no pregunta por request.method

@login_required
def producto_eliminar(request, pk):                        # DELETE
    producto = get_object_or_404(Producto, pk=pk)          # Buscamos el producto o mostramos 404

    if request.method == "POST":                           # ¿Presionó "Sí, eliminar"?
        nombre = producto.nombre                           # Guardamos el nombre para el mensaje
        producto.delete()                                  # DELETE del producto y de sus filas en la tabla intermedia
        messages.success(request, f"Producto «{nombre}» eliminado.")   # (la marca y las categorías NO se borran)
        return redirect("facturacion:producto_lista")

    # Llegó por GET: mostramos la pregunta "¿Seguro?"
    contexto = {"titulo": "Eliminar producto", "producto": producto}
    return render(request, "facturacion/producto_eliminar.html", contexto)


@login_required
def categoria_lista(request):                              # READ: solo atiende GET
    # GET: llega al abrir la página o al presionar "Buscar" (el form del buscador es method="get")
    q = request.GET.get("q", "")                           # 1. Texto del buscador: /categorias/?q=lap (si no hay, "")
    categorias = Categoria.objects.prefetch_related("productos")   # 2. Todas + sus productos en UNA consulta extra
    if q:                                                  # 3. Si buscó algo...
        categorias = categorias.filter(nombre__icontains=q)   # ...solo las que contienen ese texto en el nombre
    contexto = {"titulo": "Categorías", "categorias": categorias, "q": q}
    return render(request, "facturacion/categoria_lista.html", contexto)


@login_required
def categoria_crear(request):                              # CREATE
    if request.method == "POST":                           # POST: presionó "Guardar"
        form = CategoriaForm(request.POST)                 # 1. Formulario lleno con lo que envió
        if form.is_valid():                                # 2. ¿Pasa clean_nombre y el unique?
            categoria = form.save()                        # 3. INSERT en facturacion_categoria
            messages.success(request, f"Categoría «{categoria.nombre}» creada correctamente.")
            return redirect("facturacion:categoria_lista") # 4. Post/Redirect/Get: F5 no la vuelve a crear
        messages.error(request, "Revisa los campos marcados en rojo.")   # POST inválido: se queda con errores
    else:                                                  # GET: abrió la página con "+ Nueva categoría"
        form = CategoriaForm()                             # Formulario vacío
    contexto = {"titulo": "Nueva categoría", "form": form, "boton": "Guardar"}
    return render(request, "facturacion/categoria_form.html", contexto)


@login_required
def categoria_editar(request, pk):                         # UPDATE. pk viene de la URL: /categorias/editar/3/
    categoria = get_object_or_404(Categoria, pk=pk)        # Buscamos la categoría o mostramos 404
    if request.method == "POST":                           # POST: presionó "Actualizar"
        form = CategoriaForm(request.POST, instance=categoria)   # Datos nuevos + la categoría que se cambia
        if form.is_valid():
            form.save()                                    # UPDATE (no INSERT, gracias a instance)
            messages.success(request, f"Categoría «{categoria.nombre}» actualizada.")
            return redirect("facturacion:categoria_lista")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:                                                  # GET: clic en "Editar"
        form = CategoriaForm(instance=categoria)           # Formulario LLENO con los datos actuales
    contexto = {"titulo": f"Editar categoría: {categoria.nombre}", "form": form, "boton": "Actualizar"}
    return render(request, "facturacion/categoria_form.html", contexto)   # El mismo template de crear


@login_required
def categoria_eliminar(request, pk):                       # DELETE
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":                           # POST: presionó "Sí, eliminar"
        nombre = categoria.nombre                          # Guardamos el nombre para el mensaje
        categoria.delete()                                 # DELETE. Sin try/except: con N:M solo se borran sus filas
                                                           # en la tabla intermedia; los productos siguen existiendo
        messages.success(request, f"Categoría «{nombre}» eliminada.")
        return redirect("facturacion:categoria_lista")
    # GET: clic en "Eliminar" → mostramos la pregunta "¿Seguro?" y a cuántos productos afecta
    contexto = {
        "titulo": "Eliminar categoría",
        "categoria": categoria,
        "total_productos": categoria.productos.count(),    # related_name="productos": camino de vuelta N:M
    }
    return render(request, "facturacion/categoria_eliminar.html", contexto)


# =====================================================================
# CLIENTES · Vistas Basadas en Funciones (VBF) · Tarea 2 (5.4)
# Base: el CRUD de Productos
# =====================================================================
@login_required
def cliente_lista(request):                                # READ con buscador y páginas · solo GET
    q = request.GET.get("q", "")                           # 1. Texto del buscador (?q=perez)
    clientes = Cliente.objects.all()                       # 2. Todos (ordenados por apellidos, nombres: Meta.ordering)
    if q:
        # 3. Reto extra: objetos Q. El | significa "O": busca en apellidos O en cédula
        clientes = clientes.filter(Q(apellidos__icontains=q) | Q(cedula__icontains=q))
    paginador = Paginator(clientes, 5)                     # 4. De 5 en 5
    page_obj = paginador.get_page(request.GET.get("page")) # 5. La página pedida (?page=2). Si es inválida, da la 1 o la última
    contexto = {"titulo": "Clientes", "page_obj": page_obj, "q": q}
    return render(request, "facturacion/cliente_lista.html", contexto)


@login_required
def cliente_detalle(request, pk):                          # READ (uno): ficha del cliente · solo GET
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, "facturacion/cliente_detalle.html", {"titulo": str(cliente), "cliente": cliente})


@login_required
def cliente_crear(request):                                # CREATE
    if request.method == "POST":                           # POST: presionó "Guardar"
        form = ClienteForm(request.POST)                   # 1. Formulario con lo que escribió
        if form.is_valid():                                # 2. ¿Pasa clean_cedula, el unique y el email?
            cliente = form.save()                          # 3. INSERT (fecha_registro se llena sola)
            messages.success(request, f"Cliente «{cliente}» creado.")
            return redirect("facturacion:cliente_lista")   # 4. Post/Redirect/Get
        messages.error(request, "Revisa los campos marcados en rojo.")   # POST inválido: se queda con errores
    else:                                                  # GET: clic en "+ Nuevo cliente"
        form = ClienteForm()                               # Formulario vacío
    contexto = {"titulo": "Nuevo cliente", "form": form, "boton": "Guardar"}
    return render(request, "facturacion/cliente_form.html", contexto)


@login_required
def cliente_editar(request, pk):                           # UPDATE
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":                           # POST: presionó "Actualizar"
        form = ClienteForm(request.POST, instance=cliente) # Datos nuevos + el cliente que se cambia
        if form.is_valid():
            form.save()                                    # UPDATE
            messages.success(request, f"Cliente «{cliente}» actualizado.")
            return redirect("facturacion:cliente_lista")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:                                                  # GET: clic en "Editar"
        form = ClienteForm(instance=cliente)               # Formulario LLENO
    contexto = {"titulo": f"Editar cliente: {cliente}", "form": form, "boton": "Actualizar"}
    return render(request, "facturacion/cliente_form.html", contexto)


@login_required
def cliente_eliminar(request, pk):                         # DELETE
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":                           # POST: presionó "Sí, eliminar"
        nombre = str(cliente)                              # Guardamos el nombre antes de borrarlo
        cliente.delete()                                   # DELETE (todavía no tiene ventas que lo protejan)
        messages.success(request, f"Cliente «{nombre}» eliminado.")
        return redirect("facturacion:cliente_lista")
    # GET: clic en "Eliminar" → pregunta "¿Seguro?"
    contexto = {"titulo": "Eliminar cliente", "cliente": cliente}
    return render(request, "facturacion/cliente_eliminar.html", contexto)


# =====================================================================
# MI PERFIL · Reto (5.5) · relación 1:1 con User
# =====================================================================
@login_required
def mi_perfil(request):                                    # Sin <int:pk>: el perfil es SIEMPRE el del usuario conectado
    # get_or_create busca el perfil de este usuario; si no existe, lo crea vacío.
    # Devuelve DOS cosas: el perfil y True/False (si lo acaba de crear)
    perfil, creado = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == "POST":                           # POST: presionó "Guardar cambios"
        form = PerfilForm(request.POST, instance=perfil)   # Mismo patrón que marca_editar: instance=perfil
        if form.is_valid():
            form.save()                                    # UPDATE del perfil (el usuario no cambia)
            messages.success(request, "Tu perfil se actualizó correctamente.")
            return redirect("facturacion:mi_perfil")       # Redirige a la MISMA página (Post/Redirect/Get)
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:                                                  # GET: abrió "Mi perfil"
        form = PerfilForm(instance=perfil)                 # Formulario LLENO con sus datos actuales
    contexto = {"titulo": "Mi perfil", "form": form, "boton": "Guardar cambios"}
    return render(request, "facturacion/mi_perfil.html", contexto)

