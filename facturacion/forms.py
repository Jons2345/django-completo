from django import forms                         # Herramientas de formularios de Django
from .models import Marca,Producto                        # El modelo del que sale el formulario


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
            "categorias": forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
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