from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from productos.models import Product
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@login_required
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        return render(request, 'carrito/carrito.html', {'productos': [], 'total': 0})
    
    # Obtener todos los productos en una sola consulta
    producto_ids = list(carrito.keys())
    productos_query = Product.objects.filter(id__in=producto_ids)
    productos_dict = {str(p.id): p for p in productos_query}
    
    productos = []
    total = 0
    
    for producto_id, cantidad in carrito.items():
        if producto := productos_dict.get(producto_id):
            subtotal = producto.price * cantidad
            total += subtotal
            productos.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
    
    return render(request, 'carrito/carrito.html', {
        'productos': productos,
        'total': total,
    })

# Usar csrf_exempt temporalmente para solucionar el problema
@csrf_exempt
@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Product, id=producto_id)
    carrito = request.session.get('carrito', {})
    producto_id = str(producto_id)  # Convertir a string para usar como clave
    
    # Obtener la cantidad del formulario o usar 1 como valor predeterminado
    cantidad = 1
    if request.method == 'POST':
        try:
            cantidad_form = int(request.POST.get('cantidad', 1))
            if cantidad_form > 0:
                cantidad = cantidad_form
        except (ValueError, TypeError):
            # Si hay un error al convertir la cantidad, usar 1
            pass
    
    # Verificar stock disponible
    if producto.stock < cantidad:
        messages.error(request, f'Solo hay {producto.stock} unidades disponibles de este producto.')
        return redirect('productos:producto', producto.id)
    
    # Añadir al carrito
    if producto_id in carrito:
        carrito[producto_id] += cantidad
    else:
        carrito[producto_id] = cantidad
    
    # Guardar en la sesión
    request.session['carrito'] = carrito
    request.session.modified = True  # Forzar que se guarde la sesión
    
    messages.success(request, f'{cantidad} unidad(es) de {producto.name} agregada(s) al carrito.')
    
    # Redirigir a la página anterior o al carrito
    referer = request.META.get('HTTP_REFERER')
    if referer and 'carrito' not in referer:
        return redirect(referer)
    else:
        return redirect('carrito:ver_carrito')

@csrf_exempt
@login_required
def agregar_ajax(request):
    if request.method == 'POST':
        try:
            producto_id = request.POST.get('product_id')
            cantidad = int(request.POST.get('quantity', 1))
            
            if not producto_id:
                return JsonResponse({'success': False, 'error': 'ID de producto no proporcionado'})
            
            producto = get_object_or_404(Product, id=producto_id)
            carrito = request.session.get('carrito', {})
            producto_id = str(producto_id)  # Convertir a string para usar como clave
            
            # Verificar stock disponible
            if producto.stock < cantidad:
                return JsonResponse({
                    'success': False, 
                    'error': f'Solo hay {producto.stock} unidades disponibles de este producto.'
                })
            
            # Añadir al carrito
            if producto_id in carrito:
                carrito[producto_id] += cantidad
            else:
                carrito[producto_id] = cantidad
            
            # Guardar en la sesión
            request.session['carrito'] = carrito
            request.session.modified = True  # Forzar que se guarde la sesión
            
            # Calcular cantidad total de productos en el carrito
            cart_count = sum(carrito.values())
            
            return JsonResponse({
                'success': True, 
                'message': f'{cantidad} unidad(es) de {producto.name} agregada(s) al carrito.',
                'cart_count': cart_count
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_id = str(producto_id)
    
    if producto_id in carrito:
        if carrito[producto_id] > 1:
            carrito[producto_id] -= 1
        else:
            del carrito[producto_id]
        
        request.session['carrito'] = carrito
        request.session.modified = True  # Forzar que se guarde la sesión
        messages.success(request, 'Producto eliminado del carrito.')
    
    return redirect('carrito:ver_carrito')

@login_required
def vaciar_carrito(request):
    """Elimina todos los productos del carrito"""
    if request.method == 'POST':
        # Vaciar el carrito
        request.session['carrito'] = {}
        request.session.modified = True
        messages.success(request, 'El carrito ha sido vaciado correctamente.')
    
    return redirect('carrito:ver_carrito')

# Vista para obtener el número total de items en el carrito
def cart_count(request):
    carrito = request.session.get('carrito', {})
    # Calcular la cantidad total sumando todas las cantidades
    count = sum(carrito.values())
    return JsonResponse({'count': count})
