from django.db import models
from .enumeraciones import *
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Perfil(models.Model):
    usuario=models.OneToOneField(User, related_name='usuario', on_delete=models.CASCADE)
    telefono=models.CharField(max_length=9, null=True)
    ciudad=models.CharField(max_length=15, choices=CIUDAD, null=True) 
    direccion=models.CharField(max_length=200, null=True)

class Arma(models.Model):
    nomb_arma=models.CharField(max_length=100, null=False, verbose_name="Nombre")
    categoria=models.CharField(max_length=50, null=False)
    calibre=models.CharField(max_length=13, choices=TIPO_calibre)
    precio=models.PositiveIntegerField(default=0, validators=[MinValueValidator(0),MaxValueValidator(999999)])
    stock=models.PositiveIntegerField(default=1, validators=[MinValueValidator(1),MaxValueValidator(99)])
    descripcion=models.TextField()
    foto_arma=models.ImageField(upload_to='armas',null=False, verbose_name="Imagen")

class CartItem(models.Model):
    arma = models.ForeignKey('Arma', on_delete=models.CASCADE, verbose_name="Arma")
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    precio_por_item = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    def subtotal(self):
        return self.cantidad * self.precio_por_item

    def __str__(self):
        return f"{self.arma} - {self.cantidad} x {self.precio_por_item}"

class Cart(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuario", related_name="carts")
    items = models.ManyToManyField(CartItem, verbose_name="Ítems", related_name="carts")

    def total(self):
        return sum([item.subtotal() for item in self.items.all()])

    def __str__(self):
        return f"Cart for {self.usuario}"
    
# Ventas
class Venta(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario")
    arma = models.ForeignKey(Arma, on_delete=models.CASCADE, verbose_name="Arma")
    cantidad = models.PositiveIntegerField()
    total_venta = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=30, choices=ESTADO, default='EN PREPARACIÓN')

    def total_venta(self):
        return self.cantidad * self.arma.precio 

    def __str__(self):
        return f"Venta {self.id} - {self.arma.nomb_arma} - {self.cantidad} unidades"