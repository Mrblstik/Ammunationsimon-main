from django import forms
from .models import *
from .enumeraciones import *
from django.contrib.auth.forms import UserCreationForm

# Usuarios
class UserForm(UserCreationForm):
    
    class Meta:
        model=User
        fields=['username', 'first_name', 'last_name', 'email','password1','password2']
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

class PerfilForm(forms.ModelForm):

    class Meta:
        model=Perfil
        fields=['telefono', 'ciudad', 'direccion']

class UpdatePerfilForm(forms.ModelForm):

    class Meta:
        model=Perfil
        fields=['telefono', 'ciudad', 'direccion']

#Armas
class ArmaForm(forms.ModelForm):

    class Meta:
        model = Arma
        fields = ['id', 'nomb_arma', 'categoria', 'calibre', 'precio', 'stock', 'descripcion', 'foto_arma']

class UpdateArmaForm(forms.ModelForm):

    class Meta:
        model = Arma
        fields = ['nomb_arma', 'categoria', 'calibre', 'precio', 'stock', 'descripcion', 'foto_arma']

# Venta
class EstadoVentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['estado'] 