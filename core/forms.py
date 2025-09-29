from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario, DuenoCafeteria


class LoginForm(AuthenticationForm):
    """Formulario de login personalizado"""
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-coffee-500',
            'placeholder': 'Nombre de usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-coffee-500',
            'placeholder': 'Contraseña'
        })
    )


class DuenoCafeteriaForm(UserCreationForm):
    """Formulario de registro para dueños de cafeterías"""
    
    # Datos personales
    first_name = forms.CharField(max_length=30, required=True, label='Nombre', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, label='Apellido', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(max_length=20, required=True, label='Teléfono Personal', widget=forms.TextInput(attrs={'class': 'form-control'}))
    cedula = forms.CharField(max_length=20, required=True, label='Cédula de Identidad', widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion_personal = forms.CharField(max_length=300, required=True, label='Dirección Personal', widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Datos de la cafetería
    nombre_cafeteria = forms.CharField(max_length=200, required=True, label='Nombre de la Cafetería', widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion_cafeteria = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), required=True, label='Descripción de la Cafetería')
    direccion_cafeteria = forms.CharField(max_length=300, required=True, label='Dirección de la Cafetería', widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono_cafeteria = forms.CharField(max_length=20, required=True, label='Teléfono de la Cafetería', widget=forms.TextInput(attrs={'class': 'form-control'}))
    horario_atencion = forms.CharField(max_length=100, initial="L-D: 8:00-20:00", label='Horario de Atención', widget=forms.TextInput(attrs={'class': 'form-control'}))
    zona = forms.CharField(max_length=50, initial="Centro", label='Zona', widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Características
    wifi = forms.BooleanField(required=False, initial=True, label='¿Tiene WiFi?')
    terraza = forms.BooleanField(required=False, label='¿Tiene Terraza?')
    estacionamiento = forms.BooleanField(required=False, label='¿Tiene Estacionamiento?')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar campos de contraseña
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.is_active = False  # El usuario estará inactivo hasta la aprobación
        
        if commit:
            user.save()
            
            # Crear el perfil de dueño de cafetería
            DuenoCafeteria.objects.create(
                user=user,
                telefono=self.cleaned_data['telefono'],
                cedula=self.cleaned_data['cedula'],
                direccion_personal=self.cleaned_data['direccion_personal'],
                nombre_cafeteria=self.cleaned_data['nombre_cafeteria'],
                descripcion_cafeteria=self.cleaned_data['descripcion_cafeteria'],
                direccion_cafeteria=self.cleaned_data['direccion_cafeteria'],
                telefono_cafeteria=self.cleaned_data['telefono_cafeteria'],
                horario_atencion=self.cleaned_data['horario_atencion'],
                zona=self.cleaned_data['zona'],
                wifi=self.cleaned_data['wifi'],
                terraza=self.cleaned_data['terraza'],
                estacionamiento=self.cleaned_data['estacionamiento'],
            )
        
        return user


class RegistroForm(UserCreationForm):
    """Formulario de registro simplificado"""
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    genero = forms.ChoiceField(
        choices=PerfilUsuario.GENERO_CHOICES,
        required=True,
        label='Género'
    )
    edad = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=120,
        label='Edad'
    )
    ciudad = forms.CharField(max_length=100, required=True, label='Ciudad')
    pais = forms.CharField(max_length=100, required=True, label='País')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2',
                  'genero', 'edad', 'ciudad', 'pais')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class PerfilForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""
    
    class Meta:
        model = PerfilUsuario
        fields = ['genero', 'edad', 'ciudad', 'pais']
        widgets = {
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
        }
