from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

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
