from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from productos.models import Product, Category
from pedidos.models import Pedido, Pago
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required

User = get_user_model()

def terms_view(request):
    """Vista para mostrar los términos y condiciones."""
    return render(request, 'terms.html')

def privacy_policy_view(request):
    """Vista para mostrar la política de privacidad."""
    return render(request, 'privacy.html')

def cotizacion_view(request):
    """Vista para mostrar el formulario de cotización."""
    return render(request, 'cotizacion.html')

@staff_member_required
def admin_dashboard_view(request):
    """Vista para mostrar el dashboard administrativo personalizado."""
    # Estadísticas generales
    total_productos = Product.objects.count()
    productos_sin_stock = Product.objects.filter(stock=0).count()
    total_categorias = Category.objects.count()
    
    # Datos de pedidos
    hoy = timezone.now().date()
    inicio_mes = datetime(hoy.year, hoy.month, 1).date()
    
    total_pedidos = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_hoy = Pedido.objects.filter(fecha_pedido__date=hoy).count()
    pedidos_mes = Pedido.objects.filter(fecha_pedido__date__gte=inicio_mes).count()
    
    # Datos de ventas
    ventas_mes = Pedido.objects.filter(
        estado='enviado', 
        fecha_pedido__date__gte=inicio_mes
    ).aggregate(total=Sum('total'))['total'] or 0
    
    ventas_promedio = Pedido.objects.filter(
        estado='enviado'
    ).aggregate(promedio=Avg('total'))['promedio'] or 0
    
    # Datos de usuarios
    total_usuarios = User.objects.count()
    usuarios_nuevos_mes = User.objects.filter(date_joined__date__gte=inicio_mes).count()
    
    # Productos más vendidos - consulta simplificada
    productos_vendidos = []
    
    # Pedidos recientes
    pedidos_recientes = Pedido.objects.all().order_by('-fecha_pedido')[:5]
    
    # Contexto para la plantilla
    context = {
        'title': 'Dashboard - Sagitario Store',
        'total_productos': total_productos,
        'productos_sin_stock': productos_sin_stock,
        'total_categorias': total_categorias,
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_hoy': pedidos_hoy,
        'pedidos_mes': pedidos_mes,
        'ventas_mes': ventas_mes,
        'ventas_promedio': ventas_promedio,
        'total_usuarios': total_usuarios,
        'usuarios_nuevos_mes': usuarios_nuevos_mes,
        'pedidos_recientes': pedidos_recientes,
        'productos_vendidos': productos_vendidos,
    }
    
    return render(request, 'admin/dashboard.html', context)