from django import forms                         # Herramientas de formularios de Django
from .models import Marca, Producto, Categoria, Cliente, Perfil                        # El modelo del que sale el formulario


class MarcaForm(forms.ModelForm):                # ModelForm: formulario construido desde un modelo

    class Meta:                                  # Configuración del formulario
        model = Marca                            # ¿De qué modelo sale? De Marca
        fields = ["nombre", "pais_origen", "activo"]   # ¿Qué campos muestra y en qué orden?
        labels = {                               # Cambia el texto de la etiqueta de un campo
            "nombre": "Nombre de la marca",
        }
        widgets = {                              # widgets: CÓMO se dibuja cada campo en HTML
            # TextInput = <input type="text">. attrs agrega atributos HTML: aquí la clase de Bootstrap
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Samsung"}),
            "pais_origen": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Corea del Sur"}),
            # CheckboxInput = <input type="checkbox">. form-check-input es la clase de Bootstrap para casillas
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        
    def clean_nombre(self):                      # Validación propia del campo "nombre" (clean_ + nombre del campo)
        nombre = self.cleaned_data["nombre"].strip()   # cleaned_data: los datos ya revisados. strip quita espacios
        if len(nombre) < 2:                      # Si tiene menos de 2 letras...
            raise forms.ValidationError("El nombre debe tener al menos 2 letras.")  # ...error en rojo bajo el campo
        return nombre.title()                    # Si está bien, lo devolvemos con la Primera Letra Mayúscula
    
class ProductoForm(forms.ModelForm):                     # NUEVO: formulario de Producto
    class Meta:
        model = Producto                                 # Sale del modelo Producto
        fields = ["nombre", "descripcion", "marca", "categorias", "precio", "stock", "activo"]  # Campos en orden
        widgets = {                                      # Cómo se dibuja cada campo en HTML
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Laptop Pro 14"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),   # Caja grande de 3 líneas
            # 1:N (ForeignKey) → lista desplegable <select>: se elige UNA sola marca
            "marca": forms.Select(attrs={"class": "form-select"}),
            # N:M (ManyToMany) → una casilla por categoría: se pueden marcar VARIAS
            "categorias": forms.CheckboxSelectMultiple(),   # Sin clase: Bootstrap encogía la caja que envuelve las casillas
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),  # Con centavos
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),    # Entero, mínimo 0
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):                 # __init__ se ejecuta al crear el formulario: ProductoForm(...)
        super().__init__(*args, **kwargs)                # Primero dejamos que Django arme el formulario normal
        # Luego cambiamos las opciones de la lista de marcas: solo las activas
        self.fields["marca"].queryset = Marca.objects.filter(activo=True)
        self.fields["marca"].empty_label = "— Elige una marca —"   # Texto de la primera opción de la lista

    def clean_precio(self):                              # Validación propia del campo precio
        precio = self.cleaned_data["precio"]             # El precio ya convertido a número por Django
        if precio <= 0:                                  # Si es 0 o negativo...
            raise forms.ValidationError("El precio debe ser mayor que 0.")   # ...error en rojo bajo el campo
        return precio       
    
    
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria                                # Sale del modelo Categoria
        fields = ["nombre", "descripcion", "activo"]     # Los 3 campos del modelo, en este orden
        labels = {
            "nombre": "Nombre de la categoría",
            "descripcion": "Descripción",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Laptops"}),
            # Textarea = caja GRANDE de varias líneas (la misma que usamos en ProductoForm)
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_nombre(self):                              # Validación propia del campo "nombre"
        nombre = self.cleaned_data["nombre"].strip()     # Quitamos espacios al inicio y al final
        if len(nombre) < 3:                              # Regla 1: mínimo 3 letras
            raise forms.ValidationError("El nombre debe tener al menos 3 letras.")
        # Regla 2: la primera letra en mayúscula. Si escribe "ofertas", lo arreglamos a "Ofertas"
        # (capitalize() pone la 1ra letra en mayúscula y el resto en minúscula)
        return nombre.capitalize()
        # OJO: que no se repita lo revisa solo el unique=True del modelo


# ---------------------------------------------------------------------
# CLIENTE · base: ProductoForm (paso 3.2)
# ---------------------------------------------------------------------
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        # Todos los campos MENOS fecha_registro: esa se llena sola (auto_now_add=True)
        fields = ["cedula", "nombres", "apellidos", "email", "telefono", "direccion"]
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 0912345678", "maxlength": "10"}),
            "nombres": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Ana María"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Pérez López"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Ej: ana@correo.com"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 0991234567"}),
            "direccion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Av. Principal 123"}),
        }

    def clean_cedula(self):                              # Validación propia de la cédula (como clean_precio)
        cedula = self.cleaned_data["cedula"].strip()     # El texto que escribió, sin espacios
        if not cedula.isdigit():                         # isdigit() → True solo si TODOS son números
            raise forms.ValidationError("La cédula debe tener solo números.")
        if len(cedula) != 10:                            # len() cuenta los caracteres
            raise forms.ValidationError("La cédula debe tener exactamente 10 dígitos.")
        return cedula                                    # Que no se repita lo revisa unique=True del modelo


# ---------------------------------------------------------------------
# PERFIL · reto 1:1. Sin el campo "usuario": ese lo pone la vista (request.user)
# ---------------------------------------------------------------------
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["cedula", "telefono", "direccion", "cargo"]   # NO va "usuario": nadie lo elige
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control", "maxlength": "10"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "cargo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Vendedor"}),
        }

