from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from .models import ListaDeseos
from productos.models import Product

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')  # Cambiado de email a username
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, '¡Bienvenido de vuelta!')
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Cambiado de 'index' a 'home'
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('home')  # Cambiado de 'index' a 'home'
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'usuarios/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, '¡Has cerrado sesión exitosamente!')
    return redirect('home')  # Cambiado de 'index' a 'home'

@login_required
def profile_view(request):
    return render(request, 'tienda/pages/auth/profile.html')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'tienda/pages/auth/password_reset.html'
    email_template_name = 'tienda/pages/auth/password_reset_email.html'
    subject_template_name = 'tienda/pages/auth/password_reset_subject.txt'
    success_url = '/auth/password-reset/done/'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'tienda/pages/auth/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'tienda/pages/auth/password_reset_confirm.html'
    success_url = '/auth/password-reset/complete/'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'tienda/pages/auth/password_reset_complete.html'

@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html', {
        'user': request.user
    })

@login_required
def toggle_lista_deseos(request):
    """Vista para agregar/remover productos de la lista de deseos mediante AJAX"""
    if request.method == 'POST':
        producto_id = request.POST.get('product_id')
        if not producto_id:
            return JsonResponse({'success': False, 'error': 'ID de producto no proporcionado'}, status=400)
        
        try:
            producto = Product.objects.get(pk=producto_id)
            
            # Verificar si el producto ya está en la lista de deseos
            wishlist_item = ListaDeseos.objects.filter(usuario=request.user, producto=producto).first()
            
            if wishlist_item:
                # Si existe, eliminarlo
                wishlist_item.delete()
                return JsonResponse({
                    'success': True, 
                    'action': 'removed', 
                    'message': 'Producto eliminado de tu lista de deseos'
                })
            else:
                # Si no existe, agregarlo
                ListaDeseos.objects.create(usuario=request.user, producto=producto)
                return JsonResponse({
                    'success': True, 
                    'action': 'added', 
                    'message': 'Producto añadido a tu lista de deseos'
                })
                
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
def mi_lista_deseos(request):
    """Vista para mostrar la lista de deseos del usuario"""
    lista_deseos = ListaDeseos.objects.filter(usuario=request.user).select_related('producto')
    
    return render(request, 'usuarios/lista_deseos.html', {
        'lista_deseos': lista_deseos
    })
