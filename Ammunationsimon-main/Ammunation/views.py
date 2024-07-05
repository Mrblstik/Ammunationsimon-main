from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Arma, Perfil, Cart, CartItem, Venta
from .forms import ArmaForm, UpdateArmaForm, UserForm, PerfilForm, UpdatePerfilForm, EstadoVentaForm
from django.contrib import messages
from os import remove, path
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.db.models import Q
from .viewmodel import MostrarDatosUsuarios

# Create your views here.
def cerrar_sesion(request):
    logout(request)
    return redirect(to='index')

def index(request):
    query = request.GET.get('q')
    calibre = request.GET.get('calibre') 
    
    if query:
        armas = Arma.objects.filter(nomb_arma__icontains=query)
        if not armas.exists():
            armas = Arma.objects.all()
    else:
        armas = Arma.objects.all()
    
    if calibre:
        armas_filtrados = armas.filter(calibre=calibre)
        if armas_filtrados.exists():
            armas = armas_filtrados
    
    datos = {
        "armas": armas
    }

    return render(request,'Ammunation/index.html', datos)

@permission_required('Ammunation.add_arma')
def adminGuns(request):
    query = request.GET.get('q')
    if query:
        armas = Arma.objects.filter(
            Q(nomb_arma__icontains=query) | 
            Q(id__icontains=query) |
            Q(categoria__icontains=query) |
            Q(calibre__icontains=query) |
            Q(precio__icontains=query) |
            Q(stock__icontains=query) |
            Q(descripcion__icontains=query)
        )
        if not armas.exists():
            armas = Arma.objects.all()
    else:
        armas = Arma.objects.all()
    
    datos = {
        "armas": armas
    }

    return render(request,'Ammunation/adminGuns.html', datos)

@permission_required('Ammunation.add_user')
def administrador(request):
    #usuarios = User.objects.all()
    perfiles = Perfil.objects.all()
    
    print("***************************")
    #print(usuarios)
    usuarios_view = []
    for per in perfiles:
        usrview = MostrarDatosUsuarios()
        nombreu=per.usuario.username
        useruser=User.objects.get(username=nombreu)
        idql=str(useruser.id)

        print(idql)
        usrview.id_usuario=idql
        usrview.username=per.usuario.username
        usrview.first_name = per.usuario.first_name
        usrview.last_name =per.usuario.last_name
        usrview.email=per.usuario.email
        usrview.date_joined=per.usuario.date_joined
        usrview.ciudad=per.ciudad
        usrview.direccion=per.direccion
        usrview.telefono=per.telefono
        #print(usrview)
        usuarios_view.append(usrview)
    
    datos={
        "usuarios":usuarios_view
        
    }
    return render(request,'Ammunation/administrador.html', datos)

def carrito(request):
    return render(request,'Ammunation/carrito.html')

@login_required
def add_to_cart(request, arma_id):
    arma = get_object_or_404(Arma, id=arma_id)
    cart, created = Cart.objects.get_or_create(usuario=request.user)

    cart_item, created = CartItem.objects.get_or_create(arma=arma, precio_por_item=arma.precio)
    if not created:
        cart_item.cantidad += 1
        cart_item.save()

    cart.items.add(cart_item)
    messages.success(request, f'{arma.nomb_arma} fue añadido a tu carrito.')

    return redirect('carrito')

@login_required
def carrito(request):
    cart, created = Cart.objects.get_or_create(usuario=request.user)
    return render(request, 'Ammunation/carrito.html', {'cart': cart})

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        cart_item.cantidad = cantidad
        cart_item.save()
        messages.success(request, 'La cantidad fue actualizada.')
    return redirect('carrito')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, 'El ítem fue eliminado del carrito.')
    return redirect('carrito')

@login_required
def process_payment(request):
    cart, created = Cart.objects.get_or_create(usuario=request.user)
    if not cart.items.exists():
        messages.error(request, 'No tienes artículos en tu carrito.')
        return redirect('carrito')

    for item in cart.items.all():
        arma = item.arma
        if item.cantidad > arma.stock:
            messages.error(request, f'No hay suficiente stock para {arma.nomb_arma}.')
            return redirect('carrito')
        
        Venta.objects.create(
                usuario=request.user,
                arma=arma,
                cantidad=item.cantidad,
                estado='EN PREPARACIÓN',
                fecha=timezone.now()
            )
        
    for item in cart.items.all():
        arma = item.arma
        arma.stock -= item.cantidad
        arma.save()

    cart.items.clear()
    
    messages.success(request, 'Pago realizado con éxito. Gracias por tu compra.')
    return redirect('carrito')

@permission_required('Ammunation.change_arma')
def modificararma(request, id):
    arma = get_object_or_404(Arma, id=id)
    form = UpdateArmaForm(instance=arma)
    
    if request.method=="POST":
        form=UpdateArmaForm(data=request.POST,files=request.FILES,instance=arma)
        if form.is_valid():
            form.save()
            messages.warning(request,"Arma modificada")
            return redirect(to="adminGuns")
    
    datos={
        "form":form,
        "arma":arma
    }

    return render(request, 'Ammunation/modificararma.html', datos)

@permission_required('Ammunation.delete_arma')
def deleteGuns(request, id):
    arma=get_object_or_404(Arma, id=id)
    
    if request.method=="POST":
        remove(path.join(str(settings.MEDIA_ROOT).replace('/media',''))+arma.foto_arma.url)
        arma.delete()
        messages.warning(request,"Arma eliminada")
        return redirect(to="adminGuns")
        
    datos={
        "arma":arma
    }

    return render(request,'Ammunation/deleteGuns.html', datos)

@permission_required('Ammunation.delete_user')
def deleteUser(request, id):
    usuario = get_object_or_404(User, id=id)
    
    if request.method == "POST":
        Perfil.objects.filter(usuario=usuario).delete()
        usuario.delete()
        messages.warning(request, "Usuario eliminado")
        return redirect(to="administrador")
        
    datos = {
        "usuario": usuario
    }

    return render(request,'Ammunation/deleteUser.html', datos)

def descriptionGuns(request, id):
    arma=get_object_or_404(Arma, id=id)
    
    datos={
        "arma":arma
    }

    return render(request,'Ammunation/descriptionGuns.html', datos)

def editarPerfil(request):
    usr = request.user
    perfil_existente = Perfil.objects.filter(usuario=usr).first()

    if request.method == "POST":
        form = PerfilForm(data=request.POST, instance=perfil_existente)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.usuario = usr
            perfil.save()
            messages.warning(request,"Perfil modificado")
            return redirect(to="perfildeusuario")
    else:
        if perfil_existente:
            form = PerfilForm(instance=perfil_existente)
        else:
            form = PerfilForm()

    datos = {"form": form}
    return render(request, 'Ammunation/editarPerfil.html', datos)

def olvidarcontraseña(request):
    return render(request,'Ammunation/olvidarcontraseña.html')


def verificaremail(request):
    return render(request,'Ammunation/verificaremail.html')

def register(request):
    form=UserForm()

    if request.method=="POST":
        form=UserForm(data=request.POST)
        if form.is_valid():

            form.save()
            usuarionuevo=get_object_or_404(User,username=form.cleaned_data["username"])
            perfil=Perfil()
            perfil.usuario=usuarionuevo
            perfil.save()
            return redirect(to="login")

    datos={
        "form":form
    }

    return render(request,'registration/register.html', datos)

@permission_required('Ammunation.add_user')
def editarusuario(request, id):
    usuario = get_object_or_404(User, id=id)
    perfil_usuario = get_object_or_404(Perfil, usuario=usuario)
    
    if request.method == "POST":
        form = UpdatePerfilForm(request.POST, instance=perfil_usuario)
        if form.is_valid():
            form.save()
            messages.warning(request, "Usuario modificado")
            return redirect('administrador')
    else:
        form = UpdatePerfilForm(instance=perfil_usuario)

    datos = {
        'form': form
    }

    return render(request,'Ammunation/editarusuario.html', datos)

def perfildeusuario(request):
    usr = request.user
    perfil_usuario, created = Perfil.objects.get_or_create(usuario=usr)
    
    datos = {
        'perfil': perfil_usuario
    }

    return render(request,'Ammunation/perfildeusuario.html', datos)

@login_required
def vistaCompras(request):
    query = request.GET.get('q')
    ventas = Venta.objects.filter(usuario=request.user).order_by('-fecha')

    if query: 
        ventas_filtradas = ventas.filter(
            Q(arma__nomb_arma__icontains=query) |
            Q(arma__calibre__icontains=query) |
            Q(cantidad__icontains=query) |
            Q(estado__icontains=query)
        )
        if ventas_filtradas.exists():
            ventas = ventas_filtradas

    datos = {
        "ventas": ventas
    }

    return render(request, 'Ammunation/vistaCompras.html', datos)


@permission_required('Ammunation.add_arma')
def vistaVender(request):
    form=ArmaForm()

    if request.method=="POST":
        form=ArmaForm(data=request.POST,files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect(to="adminGuns")
        
    datos={
        "form":form
    }

    return render(request,'Ammunation/vistaVender.html', datos)

@permission_required('Ammunation.view_venta')
def vistaVentas(request):
    query = request.GET.get('q')
    ventas = Venta.objects.all().order_by('-fecha')

    if query:
        ventas_filtradas = ventas.filter(
            Q(id__icontains=query) |
            Q(arma__id__icontains=query) |
            Q(arma__nomb_arma__icontains=query) |
            Q(arma__calibre__icontains=query) |
            Q(cantidad__icontains=query) |
            Q(usuario__username__icontains=query) |
            Q(usuario__email__icontains=query) |
            Q(estado__icontains=query) |
            Q(fecha__icontains=query)
        )
        if ventas_filtradas.exists():
            ventas = ventas_filtradas

    if request.method == 'POST':
        venta_id = request.POST.get('venta_id')
        venta = get_object_or_404(Venta, id=venta_id)
        form = EstadoVentaForm(request.POST, instance=venta)
        if form.is_valid():
            form.save()
            return redirect('vistaVentas')
    else:
        form = EstadoVentaForm()

    datos={
        'ventas': ventas,
        'form': form
    }

    return render(request, 'Ammunation/vistaVentas.html', datos) 
