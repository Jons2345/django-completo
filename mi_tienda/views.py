from django.contrib import messages                       # Mensajes de éxito
from django.contrib.auth import login, logout                     # NUEVO: login() abre la sesión de un usuario
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm    # NUEVO: formulario de registro que trae Django
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect             # NUEVO: redirect
from django.utils.http import url_has_allowed_host_and_scheme  
from django.views.decorators.http import require_POST     


def saludo(request):
    return HttpResponse("<h1>¡Hola desde Django!</h1><p>Esto es un HttpResponse.</p>")


def info_peticion(request):
    datos = {
        "metodo": request.method,
        "ruta": request.path,
        "parametros_get": request.GET.dict(),
        "navegador": request.headers.get("User-Agent", ""),
        # NUEVO: request.user dice quién está conectado. Si nadie, decimos "anónimo"
        "usuario": request.user.username if request.user.is_authenticated else "anónimo",
    }
    return JsonResponse(datos)


def home(request):
    nombre = ""
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
    contexto = {
        "titulo": "Mi Tienda",
        "nombre": nombre,
        "productos": ["Laptop", "Mouse", "Teclado"],
    }
    return render(request, "home.html", contexto)


def registro(request):                                    # Crear cuenta
    if request.user.is_authenticated:                     # Si ya inició sesión, no tiene sentido registrarse...
        return redirect("home")                           # ...lo enviamos al inicio

    if request.method == "POST":                          # ¿Presionó "Crear cuenta"?
        form = UserCreationForm(request.POST)             # Llenamos el formulario con lo que escribió
        if form.is_valid():                               # ¿Usuario libre y claves iguales y seguras?
            usuario = form.save()                         # Crea el usuario con la contraseña CIFRADA
            login(request, usuario)                       # Abre su sesión de una vez
            messages.success(request, f"¡Bienvenido, {usuario.username}! Tu cuenta fue creada.")
            return redirect("home")                       # Va al inicio
    else:                                                 # Llegó por GET...
        form = UserCreationForm()                         # ...formulario vacío

    return render(request, "registration/registro.html", {"form": form})   # Muestra el formulario

def ingresar(request):                                    # LOGIN. No se llama "login" para no chocar con login() de Django
    if request.user.is_authenticated:                     # Si ya inició sesión...
        return redirect("home")                           # ...no tiene sentido mostrarle el login
    # next = la página que quería ver (GET: viene en la URL; POST: en el campo oculto)
    siguiente = request.POST.get("next") or request.GET.get("next") or ""
 
    if request.method == "POST":                          # ¿Presionó "Ingresar"?
        form = AuthenticationForm(request, data=request.POST)   # OJO: primero request y luego data=
        if form.is_valid():                               # ¿Existe el usuario y la clave es correcta?
            usuario = form.get_user()                     # El usuario que se identificó
            login(request, usuario)                       # Abre la sesión (cookie)
            messages.success(request, f"Hola, {usuario.username}.")
            # Volvemos a "next" solo si es una dirección de nuestro propio sitio
            if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
                return redirect(siguiente)
            return redirect("home")                       # Si no hay next, al inicio
    else:                                                 # Llegó por GET...
        form = AuthenticationForm(request)                # ...formulario vacío
 
    return render(request, "registration/login.html", {"form": form, "next": siguiente})
 
 
@require_POST                                             # Solo acepta POST. Un GET → error 405
def salir(request):                                       # LOGOUT
    logout(request)                                       # Cierra la sesión
    messages.info(request, "Cerraste sesión.")            # Mensaje azul
    return redirect("login")                              # Al formulario de login
 
 
def registro(request):                                    # Crear cuenta
    if request.user.is_authenticated:                     # Si ya inició sesión, no tiene sentido registrarse...
        return redirect("home")                           # ...lo enviamos al inicio
 
    if request.method == "POST":                          # ¿Presionó "Crear cuenta"?
        form = UserCreationForm(request.POST)             # Llenamos el formulario con lo que escribió
        if form.is_valid():                               # ¿Usuario libre y claves iguales y seguras?
            usuario = form.save()                         # Crea el usuario con la contraseña CIFRADA
            login(request, usuario)                       # Abre su sesión de una vez
            messages.success(request, f"¡Bienvenido, {usuario.username}! Tu cuenta fue creada.")
            return redirect("home")                       # Va al inicio
    else:                                                 # Llegó por GET...
        form = UserCreationForm()                         # ...formulario vacío
 
    return render(request, "registration/registro.html", {"form": form})   # Muestra el formulario