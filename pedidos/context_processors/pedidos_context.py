from pedidos.models import Pedido

def pedidos_count(request):
    """
    Context processor que añade el contador de pedidos pendientes
    a todas las plantillas.
    
    Añade la variable 'pending_orders_count' al contexto.
    """
    context = {
        'pending_orders_count': 0
    }
    
    if request.user.is_authenticated:
        # Contar pedidos pendientes o en proceso
        context['pending_orders_count'] = Pedido.objects.filter(
            usuario=request.user,
            estado__in=['pendiente', 'pagado', 'en_preparacion']
        ).count()
        
    return context