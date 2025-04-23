"""
URL configuration for sagitariostore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from productos.views import home
from .views import terms_view, privacy_policy_view

urlpatterns = [
    path('', home, name='home'),  # URL directa para la página principal
    path('admin/', admin.site.urls),
    path('productos/', include('productos.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('carrito/', include('carrito.urls')),  # Agregando las URLs del carrito
    path('terminos-y-condiciones/', terms_view, name='terms'),  # URL para términos y condiciones
    path('politica-de-privacidad/', privacy_policy_view, name='privacy'),  # URL para política de privacidad
]

# Agregar configuración para servir archivos multimedia en desarrollo
if settings.DEBUG:
    # Los archivos estáticos son servidos automáticamente por runserver cuando DEBUG=True
    # No es necesario añadir static(settings.STATIC_URL, ...) aquí.
    # Servir archivos multimedia
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
