from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from productos.models import Product

@login_required
def carrito_view(request):
    # Temporalmente solo renderiza la página
    return render(request, 'pedidos/carrito.html')

@login_required
def checkout_view(request):
    carrito = request.session.get('carrito', {})
    cart_items = []
    total = 0
    
    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Product, id=producto_id)
        subtotal = producto.price * cantidad
        total += subtotal
        cart_items.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal
        })
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    
    return render(request, 'pedidos/checkout.html', context)

@login_required
def mis_pedidos_view(request):
    # Temporalmente solo renderiza la página
    return render(request, 'pedidos/mis_pedidos.html')
