from django.contrib import admin
from .models import Arma, Venta

class AdmArma(admin.ModelAdmin):
    list_display=['nomb_arma', 'categoria', 'calibre', 'precio', 'stock', 'descripcion', 'foto_arma']
    list_filter=['calibre']

class AdmVenta(admin.ModelAdmin):
    list_display=['usuario', 'arma', 'cantidad', 'total_venta', 'fecha', 'estado']

# Register your models here.
admin.site.register(Arma, AdmArma)
admin.site.register(Venta, AdmVenta)