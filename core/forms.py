from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario


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
