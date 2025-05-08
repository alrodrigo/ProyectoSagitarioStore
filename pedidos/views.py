from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import Http404, JsonResponse
from productos.models import Product
from .models import DireccionEnvio, MetodoEnvio, Pedido, ItemPedido, SeguimientoPedido, Pago, Reserva
from .forms import DireccionEnvioForm, MetodoEnvioForm, MetodoPagoForm, NotasForm, ReservaForm
from django.utils import timezone

@login_required
def carrito_view(request):
    # Temporalmente solo renderiza la página
    return render(request, 'pedidos/carrito.html')

@login_required
def checkout_paso1(request):
    """
    Primer paso del checkout: Selección o creación de dirección de envío
    """
    # Obtener las direcciones del usuario
    direcciones = DireccionEnvio.objects.filter(usuario=request.user)
    
    # Verificar si hay productos en el carrito
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío. Agrega productos antes de continuar.')
        return redirect('carrito:ver_carrito')
    
    # Si se está creando una nueva dirección
    if request.method == 'POST':
        # Validar si se está seleccionando una dirección existente
        if 'direccion_id' in request.POST:
            direccion_id = request.POST.get('direccion_id')
            try:
                direccion = DireccionEnvio.objects.get(id=direccion_id, usuario=request.user)
                # Guardar el ID de la dirección en la sesión para el siguiente paso
                request.session['checkout_direccion_id'] = direccion.id
                return redirect('pedidos:checkout_paso2')
            except DireccionEnvio.DoesNotExist:
                messages.error(request, 'La dirección seleccionada no es válida.')
        
        # Si se está creando una nueva dirección
        else:
            form = DireccionEnvioForm(request.POST)
            if form.is_valid():
                # Crear la dirección sin guardarla aún
                direccion = form.save(commit=False)
                direccion.usuario = request.user
                
                # Si esta es la predeterminada, desmarcar las demás
                if direccion.es_predeterminada:
                    DireccionEnvio.objects.filter(usuario=request.user, es_predeterminada=True).update(es_predeterminada=False)
                    
                direccion.save()
                request.session['checkout_direccion_id'] = direccion.id
                messages.success(request, 'Dirección de envío guardada correctamente.')
                return redirect('pedidos:checkout_paso2')
    else:
        # Si el usuario tiene una dirección predeterminada, usarla como inicial
        try:
            direccion_predeterminada = direcciones.get(es_predeterminada=True)
            form = DireccionEnvioForm(instance=direccion_predeterminada)
        except DireccionEnvio.DoesNotExist:
            form = DireccionEnvioForm()
    
    # Calcular el total del carrito para mostrar el resumen
    total = 0
    cart_items = []
    for producto_id, cantidad in carrito.items():
        try:
            producto = Product.objects.get(id=producto_id)
            subtotal = producto.price * cantidad
            total += subtotal
            cart_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            continue
    
    context = {
        'form': form,
        'direcciones': direcciones,
        'cart_items': cart_items,
        'total': total,
        'paso_actual': 1,
    }
    
    return render(request, 'pedidos/checkout/paso1_direccion.html', context)

@login_required
def checkout_paso2(request):
    """
    Segundo paso del checkout: Selección de método de envío y pago
    """
    # Verificar que se haya completado el paso 1
    direccion_id = request.session.get('checkout_direccion_id')
    if not direccion_id:
        messages.warning(request, 'Por favor completa el paso anterior.')
        return redirect('pedidos:checkout_paso1')
    
    try:
        direccion = DireccionEnvio.objects.get(id=direccion_id, usuario=request.user)
    except DireccionEnvio.DoesNotExist:
        messages.error(request, 'La dirección seleccionada no es válida.')
        return redirect('pedidos:checkout_paso1')
    
    # Procesar formularios si es POST
    if request.method == 'POST':
        envio_form = MetodoEnvioForm(request.POST)
        pago_form = MetodoPagoForm(request.POST)
        
        if envio_form.is_valid() and pago_form.is_valid():
            # Guardar datos en sesión para el siguiente paso
            metodo_envio_id = envio_form.cleaned_data['metodo_envio'].id
            request.session['checkout_envio_id'] = metodo_envio_id
            request.session['checkout_pago'] = pago_form.cleaned_data['metodo_pago']
            request.session['checkout_referencia'] = pago_form.cleaned_data.get('referencia_pago', '')
            
            return redirect('pedidos:checkout_paso3')
    else:
        envio_form = MetodoEnvioForm()
        pago_form = MetodoPagoForm()
    
    # Obtener el carrito para mostrar el resumen
    carrito = request.session.get('carrito', {})
    total = 0
    cart_items = []
    
    for producto_id, cantidad in carrito.items():
        try:
            producto = Product.objects.get(id=producto_id)
            subtotal = producto.price * cantidad
            total += subtotal
            cart_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            continue
    
    # Obtener los métodos de envío disponibles para calcular el costo total con envío
    metodos_envio = MetodoEnvio.objects.filter(activo=True)
    
    context = {
        'direccion': direccion,
        'envio_form': envio_form,
        'pago_form': pago_form,
        'cart_items': cart_items,
        'subtotal': total,
        'total': total,  # Agregamos el total para que esté disponible en la plantilla
        'metodos_envio': metodos_envio,
        'paso_actual': 2,
    }
    
    return render(request, 'pedidos/checkout/paso2_envio_pago.html', context)

@login_required
def checkout_paso3(request):
    """
    Tercer paso del checkout: Revisión y confirmación del pedido
    """
    # Verificar que se hayan completado los pasos anteriores
    direccion_id = request.session.get('checkout_direccion_id')
    envio_id = request.session.get('checkout_envio_id')
    metodo_pago = request.session.get('checkout_pago')
    
    if not all([direccion_id, envio_id, metodo_pago]):
        messages.warning(request, 'Por favor completa los pasos anteriores.')
        return redirect('pedidos:checkout_paso1')
    
    try:
        direccion = DireccionEnvio.objects.get(id=direccion_id, usuario=request.user)
        metodo_envio = MetodoEnvio.objects.get(id=envio_id, activo=True)
    except (DireccionEnvio.DoesNotExist, MetodoEnvio.DoesNotExist):
        messages.error(request, 'Algunos datos del pedido no son válidos.')
        return redirect('pedidos:checkout_paso1')
    
    # Formulario para notas adicionales
    if request.method == 'POST':
        notas_form = NotasForm(request.POST)
        if notas_form.is_valid():
            # Crear el pedido
            return crear_pedido(request, direccion, metodo_envio, metodo_pago, notas_form.cleaned_data.get('notas', ''))
    else:
        notas_form = NotasForm()
    
    # Obtener el carrito para mostrar el resumen
    carrito = request.session.get('carrito', {})
    subtotal = 0
    cart_items = []
    
    for producto_id, cantidad in carrito.items():
        try:
            producto = Product.objects.get(id=producto_id)
            precio_item = producto.price * cantidad
            subtotal += precio_item
            cart_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': precio_item
            })
        except Product.DoesNotExist:
            continue
    
    # Calcular el total con envío
    costo_envio = metodo_envio.precio
    total = subtotal + costo_envio
    
    context = {
        'direccion': direccion,
        'metodo_envio': metodo_envio,
        'metodo_pago': dict(Pedido.METODO_PAGO_CHOICES).get(metodo_pago),
        'referencia_pago': request.session.get('checkout_referencia', ''),
        'cart_items': cart_items,
        'subtotal': subtotal,
        'costo_envio': costo_envio,
        'total': total,
        'notas_form': notas_form,
        'paso_actual': 3,
    }
    
    return render(request, 'pedidos/checkout/paso3_confirmacion.html', context)

@login_required
def crear_pedido(request, direccion, metodo_envio, metodo_pago, notas=''):
    """
    Función para crear el pedido una vez confirmados todos los datos
    """
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('carrito:ver_carrito')
    
    # Calcular subtotal
    subtotal = 0
    items_pedido = []
    
    # Verificar stock y crear items del pedido
    for producto_id, cantidad in carrito.items():
        try:
            producto = Product.objects.get(id=producto_id)
            
            # Verificar si hay suficiente stock
            if producto.stock < cantidad:
                messages.error(request, f'No hay suficiente stock de {producto.name}. Solo quedan {producto.stock} unidades.')
                return redirect('pedidos:checkout_paso3')
            
            precio_item = producto.price
            subtotal_item = precio_item * cantidad
            subtotal += subtotal_item
            
            # Guardar información del item para crear después
            items_pedido.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio': precio_item,
                'subtotal': subtotal_item
            })
            
        except Product.DoesNotExist:
            # Si el producto no existe, simplemente lo ignoramos
            continue
    
    # Si no hay productos válidos, redirigir
    if not items_pedido:
        messages.warning(request, 'No se encontraron productos válidos en tu carrito.')
        return redirect('carrito:ver_carrito')
    
    # Crear el pedido
    costo_envio = metodo_envio.precio
    total = subtotal + costo_envio
    
    pedido = Pedido.objects.create(
        usuario=request.user,
        direccion_envio=direccion,
        metodo_envio=metodo_envio,
        metodo_pago=metodo_pago,
        referencia_pago=request.session.get('checkout_referencia', ''),
        subtotal=subtotal,
        costo_envio=costo_envio,
        total=total,
        notas=notas,
    )
    
    # Crear los items del pedido y actualizar stock
    for item in items_pedido:
        ItemPedido.objects.create(
            pedido=pedido,
            producto=item['producto'],
            cantidad=item['cantidad'],
            precio=item['precio'],
            subtotal=item['subtotal']
        )
        
        # Actualizar el stock del producto
        producto = item['producto']
        producto.stock -= item['cantidad']
        producto.save()
    
    # Crear el primer seguimiento del pedido
    SeguimientoPedido.objects.create(
        pedido=pedido,
        estado='pendiente',
        descripcion='Pedido creado correctamente'
    )
    
    # Procesar el pago
    from .services.payment_service import get_payment_processor
    
    # Datos adicionales para el pago
    datos_pago = {
        'referencia': request.session.get('checkout_referencia', ''),
        'user_id': request.user.id,
        'user_email': request.user.email
    }
    
    # Obtener el procesador adecuado según el método de pago
    payment_processor = get_payment_processor(metodo_pago)
    
    # Procesar el pago
    payment_result = payment_processor.process_payment(
        pedido_id=pedido.id,
        metodo_pago=metodo_pago,
        datos=datos_pago
    )
    
    # Guardar el ID del pago en sesión para mostrarlo en la confirmación
    if payment_result['success']:
        request.session['payment_id'] = payment_result['payment_id']
        request.session['payment_status'] = payment_result.get('status', 'pending')
        request.session['payment_message'] = payment_result.get('message', '')
    else:
        request.session['payment_error'] = payment_result.get('error', 'unknown_error')
        request.session['payment_message'] = payment_result.get('message', 'Error al procesar el pago')
    
    # Limpiar el carrito y los datos de checkout de la sesión
    request.session['carrito'] = {}
    for key in list(request.session.keys()):
        if key.startswith('checkout_'):
            del request.session[key]
    request.session.modified = True
    
    # Mostrar mensaje de éxito
    messages.success(request, '¡Pedido realizado con éxito!')
    
    # Redirigir a la página de confirmación
    return redirect('pedidos:confirmacion_pedido', pedido_id=pedido.id)

@login_required
def confirmacion_pedido(request, pedido_id):
    """
    Vista de confirmación después de realizar un pedido
    """
    try:
        pedido = Pedido.objects.get(id=pedido_id, usuario=request.user)
    except Pedido.DoesNotExist:
        raise Http404("El pedido no existe")
    
    # Obtener información de pago de la sesión o del pedido
    payment_id = request.session.pop('payment_id', None)
    payment_status = request.session.pop('payment_status', None)
    payment_message = request.session.pop('payment_message', None)
    payment_error = request.session.pop('payment_error', None)
    
    # Si hay un pago asociado con el pedido, obtener su información
    try:
        pago = pedido.pago
        if not payment_status:
            payment_status = pago.estado
    except:
        pago = None
    
    context = {
        'pedido': pedido,
        'items': pedido.items.all(),
        'pago': pago,
        'payment_status': payment_status,
        'payment_message': payment_message,
        'payment_error': payment_error,
    }
    
    return render(request, 'pedidos/checkout/confirmacion_pedido.html', context)

@login_required
def mis_pedidos(request):
    """
    Vista para ver todos los pedidos del usuario
    """
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    
    context = {
        'pedidos': pedidos,
    }
    
    return render(request, 'pedidos/mis_pedidos.html', context)

@login_required
def detalle_pedido(request, pedido_id):
    """
    Vista de detalle de un pedido específico
    """
    try:
        pedido = Pedido.objects.get(id=pedido_id, usuario=request.user)
        # Eliminamos el mensaje de depuración que causa confusión
    except Pedido.DoesNotExist:
        raise Http404("El pedido no existe")
    
    # Usar .select_related('pedido') para optimizar consultas
    seguimientos = pedido.seguimientos.all().order_by('-fecha')
    
    # SOLUCIÓN: Verificar y actualizar el historial de seguimiento si es necesario
    if pedido.estado == 'pagado' and not seguimientos.filter(estado='pagado').exists():
        # Crear el registro de seguimiento para "pagado" si no existe
        nuevo_seguimiento = SeguimientoPedido.objects.create(
            pedido=pedido,
            estado='pagado',
            descripcion='Pago confirmado. Pedido listo para preparación.'
        )
        messages.success(request, "Se ha actualizado el historial de seguimiento del pedido.")
        # Refrescar la lista de seguimientos después de crear uno nuevo
        seguimientos = list(pedido.seguimientos.all().order_by('-fecha'))
    
    # Calcular las clases para cada etapa basándose SOLO en el estado actual del pedido
    progress_class = 'progress-width-0'  # Clase CSS por defecto
    step_classes = {
        'step_pendiente': '',
        'step_pagado': '',
        'step_en_preparacion': '',
        'step_enviado': '',
        'step_entregado': '',
    }
    
    # Determinar el ancho de la barra de progreso según el estado ACTUAL del pedido
    if pedido.estado == 'pendiente':
        progress_class = 'progress-width-0'
        step_classes['step_pendiente'] = 'step-active'
    elif pedido.estado == 'pagado':
        progress_class = 'progress-width-25'
        step_classes['step_pendiente'] = 'step-completed'
        step_classes['step_pagado'] = 'step-active'
    elif pedido.estado == 'en_preparacion':
        progress_class = 'progress-width-50'
        step_classes['step_pendiente'] = 'step-completed'
        step_classes['step_pagado'] = 'step-completed'
        step_classes['step_en_preparacion'] = 'step-active'
    elif pedido.estado == 'enviado':
        progress_class = 'progress-width-75'
        step_classes['step_pendiente'] = 'step-completed'
        step_classes['step_pagado'] = 'step-completed'
        step_classes['step_en_preparacion'] = 'step-completed'
        step_classes['step_enviado'] = 'step-active'
    elif pedido.estado == 'entregado':
        progress_class = 'progress-width-100'
        step_classes['step_pendiente'] = 'step-completed'
        step_classes['step_pagado'] = 'step-completed'
        step_classes['step_en_preparacion'] = 'step-completed'
        step_classes['step_enviado'] = 'step-completed'
        step_classes['step_entregado'] = 'step-active'
    elif pedido.estado == 'cancelado':
        progress_class = 'progress-width-100'
        step_classes['step_entregado'] = 'step-failed'
    
    context = {
        'pedido': pedido,
        'items': pedido.items.all(),
        'seguimientos': seguimientos,
        'progress_class': progress_class,
        'step_classes': step_classes,
        # Agregar variables adicionales para asegurar la correcta visualización
        'estado_actual': pedido.estado,
        'es_pagado': pedido.estado == 'pagado',
        'es_preparacion': pedido.estado == 'en_preparacion',
        'es_enviado': pedido.estado == 'enviado',
        'es_entregado': pedido.estado == 'entregado',
        'es_cancelado': pedido.estado == 'cancelado',
    }
    
    return render(request, 'pedidos/detalle_pedido.html', context)

@login_required
def editar_direccion(request, direccion_id):
    """
    Vista para editar una dirección de envío existente
    """
    try:
        direccion = DireccionEnvio.objects.get(id=direccion_id, usuario=request.user)
    except DireccionEnvio.DoesNotExist:
        messages.error(request, 'La dirección solicitada no existe o no tienes permisos para editarla.')
        return redirect('pedidos:checkout_paso1')
    
    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección actualizada correctamente.')
            
            # Redirigir de vuelta a la página que corresponda según el contexto
            next_url = request.GET.get('next', 'pedidos:checkout_paso1')
            return redirect(next_url)
    else:
        form = DireccionEnvioForm(instance=direccion)
    
    context = {
        'form': form,
        'direccion': direccion,
        'edit_mode': True,
    }
    
    return render(request, 'pedidos/direccion_form.html', context)

@login_required
def eliminar_direccion(request, direccion_id):
    """
    Vista para eliminar una dirección de envío
    """
    try:
        direccion = DireccionEnvio.objects.get(id=direccion_id, usuario=request.user)
        
        # Verificar que no sea la dirección predeterminada
        if direccion.es_predeterminada:
            messages.error(request, 'No puedes eliminar tu dirección predeterminada. Establece otra como predeterminada primero.')
        else:
            # Solo permitir eliminar mediante POST para evitar eliminaciones accidentales
            if request.method == 'POST':
                direccion.delete()
                messages.success(request, 'Dirección eliminada correctamente.')
            else:
                messages.error(request, 'Método no permitido para eliminar direcciones.')
    except DireccionEnvio.DoesNotExist:
        messages.error(request, 'La dirección solicitada no existe o no tienes permisos para eliminarla.')
    
    # Redirigir de vuelta a la página que corresponda según el contexto
    next_url = request.GET.get('next', 'pedidos:checkout_paso1')
    return redirect(next_url)

@login_required
def subir_comprobante(request, pago_id):
    """
    Permite al usuario subir un comprobante de pago
    """
    try:
        # Asegurarnos de que el pago pertenece al usuario actual
        pago = Pago.objects.get(id=pago_id, pedido__usuario=request.user)
        
        if request.method == 'POST':
            # Verificar si el pago ya está marcado como completado
            if pago.estado == 'completado':
                messages.warning(request, 'Este pago ya ha sido completado anteriormente.')
                return redirect('pedidos:confirmacion_pedido', pedido_id=pago.pedido.id)
            
            # Procesamos la imagen del comprobante
            comprobante = request.FILES.get('comprobante')
            if comprobante:
                pago.comprobante = comprobante
                pago.estado = 'procesando'  # Cambiamos el estado a procesando mientras se verifica
                pago.save()
                
                # Crear un registro en el seguimiento
                SeguimientoPedido.objects.create(
                    pedido=pago.pedido,
                    estado=pago.pedido.estado,
                    descripcion='Comprobante de pago cargado. En proceso de verificación.'
                )
                
                messages.success(request, 'Comprobante subido correctamente. Tu pago será verificado en breve.')
            else:
                messages.error(request, 'No se ha seleccionado ningún archivo.')
                
            return redirect('pedidos:confirmacion_pedido', pedido_id=pago.pedido.id)
    except Pago.DoesNotExist:
        messages.error(request, 'No se encontró el pago solicitado.')
        return redirect('pedidos:mis_pedidos')
    
    # Si es GET o hay algún error, redirigir a confirmación
    return redirect('pedidos:confirmacion_pedido', pedido_id=pago.pedido.id)

@login_required
def verificar_pago(request, pedido_id):
    """
    Vista para verificar el estado actual de un pago mediante AJAX
    """
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Si no es una petición AJAX, redirigir a la página del pedido
        return redirect('pedidos:confirmacion_pedido', pedido_id=pedido_id)
    
    try:
        # Verificar que el pedido pertenezca al usuario actual
        pedido = Pedido.objects.get(id=pedido_id, usuario=request.user)
        
        # Intentar obtener el pago asociado
        try:
            pago = pedido.pago
            estado = pago.estado
            
            # Personalizar mensaje según el estado
            if estado == 'completado':
                mensaje = "El pago ha sido procesado correctamente."
            elif estado == 'procesando':
                mensaje = "Tu pago está siendo verificado. Te notificaremos cuando sea confirmado."
            elif estado == 'fallido':
                mensaje = "Ha ocurrido un problema con el pago. Por favor, intenta nuevamente."
            else:  # pendiente
                if pago.metodo_pago == 'qr':
                    mensaje = "Estamos esperando la confirmación de tu pago por QR."
                elif pago.metodo_pago == 'transferencia':
                    mensaje = "Estamos esperando la confirmación de tu transferencia bancaria."
                else:
                    mensaje = "Tu pago está pendiente de confirmación."
            
            return JsonResponse({
                'success': True,
                'estado': estado,
                'mensaje': mensaje
            })
            
        except Exception as e:
            # Si no hay pago asociado o hay un error
            return JsonResponse({
                'success': True,
                'estado': 'pendiente',
                'mensaje': "No se encontró información actualizada sobre el pago."
            })
            
    except Pedido.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': "No se encontró el pedido solicitado."
        }, status=404)

# Vistas para el sistema de reservas

@login_required
def mis_reservas(request):
    """
    Muestra todas las reservas del usuario actual
    """
    reservas = Reserva.objects.filter(usuario=request.user).order_by('-fecha_solicitud')
    
    # Agrupar reservas por estado para facilitar la visualización
    reservas_activas = reservas.filter(estado__in=['solicitada', 'confirmada', 'pagada', 'lista'])
    reservas_completadas = reservas.filter(estado='convertida')
    reservas_canceladas = reservas.filter(estado='cancelada')
    
    context = {
        'reservas_activas': reservas_activas,
        'reservas_completadas': reservas_completadas,
        'reservas_canceladas': reservas_canceladas,
        'total_reservas': reservas.count(),
    }
    
    return render(request, 'pedidos/reservas/mis_reservas.html', context)

@login_required
def detalle_reserva(request, reserva_id):
    """
    Muestra los detalles de una reserva específica
    """
    try:
        reserva = Reserva.objects.select_related('pedido_creado').get(id=reserva_id, usuario=request.user)
    except Reserva.DoesNotExist:
        messages.error(request, 'La reserva solicitada no existe o no tienes permiso para verla.')
        return redirect('pedidos:mis_reservas')
    
    # Si la reserva ha sido convertida a pedido, verificar que el pedido exista
    pedido = None
    if reserva.estado == 'convertida' and reserva.pedido_creado:
        pedido = reserva.pedido_creado
    
    context = {
        'reserva': reserva,
        'pedido': pedido,
        'estados_badges': {
            'solicitada': 'badge-info',
            'confirmada': 'badge-primary',
            'anticipo_pendiente': 'badge-warning',
            'pagada': 'badge-success',
            'lista': 'badge-warning',
            'convertida': 'badge-secondary',
            'cancelada': 'badge-danger',
        }
    }
    
    return render(request, 'pedidos/reservas/detalle_reserva.html', context)

@login_required
def solicitar_reserva(request, producto_id):
    """
    Permite al usuario solicitar una reserva para un producto
    """
    try:
        producto = Product.objects.get(id=producto_id)
    except Product.DoesNotExist:
        messages.error(request, 'El producto solicitado no existe.')
        return redirect('productos:lista_productos')
    
    # Verificar si el usuario ya tiene una reserva activa para este producto
    reserva_existente = Reserva.objects.filter(
        usuario=request.user,
        producto=producto,
        estado__in=['solicitada', 'confirmada', 'pagada', 'lista']
    ).first()
    
    if reserva_existente:
        messages.warning(request, f'Ya tienes una reserva activa para este producto (#{reserva_existente.id}).')
        return redirect('pedidos:detalle_reserva', reserva_id=reserva_existente.id)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.producto = producto
            reserva.monto_total = producto.price * reserva.cantidad
            reserva.save()
            
            messages.success(request, 'Tu solicitud de reserva ha sido enviada. Te notificaremos cuando sea confirmada.')
            return redirect('pedidos:detalle_reserva', reserva_id=reserva.id)
    else:
        form = ReservaForm()
    
    context = {
        'form': form,
        'producto': producto,
        'precio_unitario': producto.price,
    }
    
    return render(request, 'pedidos/reservas/solicitar_reserva.html', context)

@login_required
def cancelar_reserva(request, reserva_id):
    """
    Permite al usuario cancelar una reserva que aún no ha sido confirmada
    """
    try:
        reserva = Reserva.objects.get(id=reserva_id, usuario=request.user)
    except Reserva.DoesNotExist:
        messages.error(request, 'La reserva solicitada no existe o no tienes permiso para cancelarla.')
        return redirect('pedidos:mis_reservas')
    
    # Solo permitir cancelar reservas en estados específicos
    if reserva.estado in ['convertida', 'cancelada']:
        messages.error(request, 'Esta reserva ya no puede ser cancelada.')
        return redirect('pedidos:detalle_reserva', reserva_id=reserva_id)
    
    # Si ya se ha pagado un anticipo, no permitir cancelación directa
    if reserva.anticipo and reserva.estado == 'pagada':
        messages.warning(request, 'No puedes cancelar esta reserva porque ya se ha pagado un anticipo. Por favor, contacta con el administrador.')
        return redirect('pedidos:detalle_reserva', reserva_id=reserva_id)
    
    # Verificar que sea una solicitud POST (para evitar cancelaciones accidentales)
    if request.method == 'POST':
        reserva.cancelar_reserva()
        messages.success(request, 'Tu reserva ha sido cancelada correctamente.')
        return redirect('pedidos:mis_reservas')
    
    # Si es una solicitud GET, mostrar página de confirmación
    context = {
        'reserva': reserva,
    }
    
    return render(request, 'pedidos/reservas/confirmar_cancelacion.html', context)

@login_required
def registrar_anticipo_reserva(request, reserva_id):
    """Vista para que el usuario registre el anticipo de una reserva"""
    try:
        reserva = Reserva.objects.get(id=reserva_id, usuario=request.user)
    except Reserva.DoesNotExist:
        messages.error(request, 'La reserva no existe o no tienes permiso para verla.')
        return redirect('pedidos:mis_reservas')
        
    if reserva.estado != 'anticipo_pendiente':
        messages.error(request, 'Esta reserva no está en estado de anticipo pendiente.')
        return redirect('pedidos:detalle_reserva', reserva_id=reserva.id)
    
    anticipo_minimo = reserva.calcular_anticipo_requerido()
    
    if request.method == 'POST':
        monto = request.POST.get('monto')
        comprobante = request.FILES.get('comprobante')
        
        if not monto or not comprobante:
            messages.error(request, 'Por favor proporciona el monto y el comprobante del anticipo.')
            return redirect('pedidos:registrar_anticipo_reserva', reserva_id=reserva.id)
        
        try:
            monto = float(monto)
            if monto < anticipo_minimo:
                messages.error(request, f'El anticipo debe ser al menos {anticipo_minimo} Bs ({reserva.porcentaje_anticipo}% del total)')
                return redirect('pedidos:registrar_anticipo_reserva', reserva_id=reserva.id)
                
            reserva.registrar_anticipo(monto, comprobante)
            messages.success(request, 'Anticipo registrado correctamente. Revisaremos tu comprobante pronto.')
            return redirect('pedidos:detalle_reserva', reserva_id=reserva.id)
            
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('pedidos:registrar_anticipo_reserva', reserva_id=reserva.id)
    
    context = {
        'reserva': reserva,
        'anticipo_minimo': anticipo_minimo,
        'fecha_limite': reserva.fecha_limite_anticipo,
    }
    
    return render(request, 'pedidos/reservas/registrar_anticipo.html', context)

@login_required
def verificar_anticipo_reserva(request, reserva_id):
    """Vista para que el admin verifique el anticipo de una reserva"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('pedidos:detalle_reserva', reserva_id=reserva_id)
        
    try:
        reserva = Reserva.objects.get(id=reserva_id)
    except Reserva.DoesNotExist:
        messages.error(request, 'La reserva no existe.')
        return redirect('admin:pedidos_reserva_changelist')
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'aprobar':
            reserva.estado = 'pagada'
            reserva.save()
            messages.success(request, 'Anticipo verificado y aprobado correctamente.')
        elif accion == 'rechazar':
            motivo = request.POST.get('motivo_rechazo')
            reserva.estado = 'anticipo_pendiente'
            if motivo:
                reserva.notas_admin = f"Anticipo rechazado: {motivo}"
            reserva.save()
            messages.warning(request, 'Anticipo rechazado. Se ha notificado al cliente.')
            
    return redirect('admin:pedidos_reserva_change', object_id=reserva.id)

@login_required
def convertir_reserva(request, reserva_id):
    """
    Convierte una reserva en estado 'lista' a un pedido formal
    """
    try:
        reserva = Reserva.objects.get(id=reserva_id, usuario=request.user)
    except Reserva.DoesNotExist:
        messages.error(request, 'La reserva no existe o no tienes permiso para verla.')
        return redirect('pedidos:mis_reservas')
    
    if reserva.estado != 'lista':
        messages.error(request, 'La reserva debe estar lista para entrega antes de convertirla a pedido.')
        return redirect('pedidos:detalle_reserva', reserva_id=reserva.id)

    try:
        # Usar el método del modelo para convertir la reserva a pedido
        pedido = reserva.convertir_a_pedido()
        messages.success(request, 'Reserva convertida a pedido exitosamente.')
        return redirect('pedidos:detalle_pedido', pedido_id=pedido.id)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('pedidos:detalle_reserva', reserva_id=reserva.id)
