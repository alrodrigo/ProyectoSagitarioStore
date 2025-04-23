from django.db import models
from django.conf import settings
from productos.models import Product
from django.utils import timezone
import uuid

class DireccionEnvio(models.Model):
    """Modelo para almacenar direcciones de envío de los usuarios"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='direcciones')
    nombre_completo = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20)
    es_predeterminada = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre_completo} - {self.ciudad}"
    
    def save(self, *args, **kwargs):
        # Si esta dirección es predeterminada, quitar el estado predeterminado de otras direcciones del usuario
        if self.es_predeterminada:
            DireccionEnvio.objects.filter(usuario=self.usuario, es_predeterminada=True).exclude(id=self.id).update(es_predeterminada=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Dirección de envío"
        verbose_name_plural = "Direcciones de envío"
        ordering = ['-es_predeterminada', '-fecha_creacion']

class MetodoEnvio(models.Model):
    """Modelo para almacenar métodos de envío disponibles"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tiempo_estimado = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.precio} Bs"
    
    class Meta:
        verbose_name = "Método de envío"
        verbose_name_plural = "Métodos de envío"

class Pedido(models.Model):
    """Modelo para almacenar pedidos de los usuarios"""
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('en_preparacion', 'En Preparación'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    
    METODO_PAGO_CHOICES = (
        ('transferencia', 'Transferencia Bancaria'),
        ('qr', 'Pago con QR'),
        ('efectivo', 'Pago en Efectivo (contra entrega)'),
        ('tigo_money', 'Tigo Money'),
    )
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    direccion_envio = models.ForeignKey(DireccionEnvio, on_delete=models.SET_NULL, null=True)
    metodo_envio = models.ForeignKey(MetodoEnvio, on_delete=models.SET_NULL, null=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    referencia_pago = models.CharField(max_length=100, blank=True, null=True)
    
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(blank=True, null=True)
    
    # Guardar el estado original para detectar cambios
    __original_estado = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_estado = self.estado

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_pedido']
        
    def actualizar_total(self):
        """Actualiza los totales del pedido basado en los items y el envío"""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.total = self.subtotal + self.costo_envio
        # No llamamos a save() aquí para evitar recursión infinita si se llama desde save()
        # self.save(update_fields=['subtotal', 'total']) # Podría ser una opción, pero mejor manejarlo fuera

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        # Comprobar si el estado ha cambiado ANTES de llamar a super().save()
        estado_cambiado = False
        if not is_new and self.pk: # Solo si el objeto ya existe en la BD
            try:
                pedido_anterior = Pedido.objects.get(pk=self.pk)
                if pedido_anterior.estado != self.estado:
                    estado_cambiado = True
            except Pedido.DoesNotExist:
                # El objeto aún no está en la BD, se tratará como nuevo
                is_new = True

        super().save(*args, **kwargs) # Guardar el pedido primero

        if not is_new and estado_cambiado:
            # Crear entrada de seguimiento automáticamente
            descripcion_seguimiento = f"Estado del pedido actualizado a: {self.get_estado_display()}."
            # Podrías añadir lógica para descripciones más específicas si quieres
            if self.estado == 'enviado':
                 descripcion_seguimiento = "El pedido ha sido enviado." # Ejemplo
            elif self.estado == 'entregado':
                 descripcion_seguimiento = "El pedido ha sido entregado." # Ejemplo
            elif self.estado == 'cancelado':
                 descripcion_seguimiento = "El pedido ha sido cancelado." # Ejemplo
            elif self.estado == 'pagado':
                 descripcion_seguimiento = "El pago del pedido ha sido confirmado." # Ejemplo

            SeguimientoPedido.objects.create(
                pedido=self,
                estado=self.estado,
                descripcion=descripcion_seguimiento
            )

        elif is_new: # Si es un pedido nuevo, crear seguimiento inicial
             SeguimientoPedido.objects.create(
                pedido=self,
                estado=self.estado, # Estado inicial (usualmente 'pendiente')
                descripcion="Pedido creado y pendiente de pago."
            )

class ItemPedido(models.Model):
    """Modelo para almacenar productos individuales en un pedido"""
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio en el momento de la compra
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        # Manejar caso donde producto es None
        nombre_producto = self.producto.name if self.producto else "[Producto Eliminado]"
        return f"{self.cantidad}x {nombre_producto} en Pedido #{self.pedido.id}"
    
    def save(self, *args, **kwargs):
        # Calcular el subtotal antes de guardar
        self.subtotal = self.precio * self.cantidad
        super().save(*args, **kwargs)
        
        # Actualizar totales del pedido DESPUÉS de guardar el item
        # Llamamos a save() aquí pero solo actualizando campos específicos para evitar recursión
        # si el save del pedido tuviera lógica compleja que llame a save de items.
        pedido = self.pedido
        pedido.subtotal = sum(item.subtotal for item in pedido.items.all())
        # Asegurarse que costo_envio no sea None antes de sumar
        costo_envio = pedido.costo_envio if pedido.costo_envio is not None else 0
        pedido.total = pedido.subtotal + costo_envio
        pedido.save(update_fields=['subtotal', 'total'])

    class Meta:
        verbose_name = "Item de pedido"
        verbose_name_plural = "Items de pedido"

class SeguimientoPedido(models.Model):
    """Modelo para almacenar actualizaciones del estado de los pedidos"""
    pedido = models.ForeignKey(Pedido, related_name='seguimientos', on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=Pedido.ESTADO_CHOICES)
    descripcion = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Seguimiento #{self.id} - Pedido #{self.pedido.id} - {self.estado}"
    
    class Meta:
        verbose_name = "Seguimiento de pedido"
        verbose_name_plural = "Seguimientos de pedidos"
        ordering = ['-fecha']

class Pago(models.Model):
    """Modelo para almacenar información de pagos"""
    ESTADO_PAGO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    )
    
    METODO_PAGO_CHOICES = Pedido.METODO_PAGO_CHOICES
    
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='pago')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='pendiente')
    referencia = models.CharField(max_length=100, blank=True, null=True)
    comprobante = models.ImageField(upload_to='comprobantes/', blank=True, null=True)
    
    # Para pagos en línea
    token_transaccion = models.CharField(max_length=255, blank=True, null=True)
    id_transaccion = models.CharField(max_length=255, blank=True, null=True)
    
    # Campo para almacenar información adicional en formato JSON
    datos_adicionales = models.JSONField(blank=True, null=True)
    
    # Campos para QR de pago (nuevo)
    qr_imagen = models.ImageField(upload_to='pagos/qr/', blank=True, null=True, 
                                verbose_name="Imagen QR de pago")
    qr_instrucciones = models.TextField(blank=True, null=True, 
                                      verbose_name="Instrucciones para pago QR")
    
    # Campos para API de pago (nuevo)
    api_callback_url = models.CharField(max_length=255, blank=True, null=True,
                                     verbose_name="URL de callback de API")
    api_webhook_recibido = models.BooleanField(default=False,
                                            verbose_name="Webhook recibido")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Pago {self.id} - Pedido #{self.pedido.id} - {self.get_estado_display()}"
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_creacion']
    
    def generar_token(self):
        """Genera un token único para la transacción"""
        return str(uuid.uuid4())
    
    def iniciar_pago(self):
        """Inicia el proceso de pago"""
        self.token_transaccion = self.generar_token()
        self.estado = 'procesando'
        self.save()
        return self.token_transaccion
    
    def completar_pago(self, id_transaccion=None, datos=None):
        """Marca el pago como completado. NO actualiza el pedido aquí."""
        estado_anterior = self.estado
        self.estado = 'completado'
        if id_transaccion:
            self.id_transaccion = id_transaccion
        if datos:
            self.datos_adicionales = datos
        self.save()

        return True
    
    def marcar_como_fallido(self, datos=None):
        """Marca el pago como fallido"""
        self.estado = 'fallido'
        if datos:
            self.datos_adicionales = datos
        self.save()
        return False

class QRPredefinido(models.Model):
    """Modelo para almacenar códigos QR predefinidos para pagos"""
    nombre = models.CharField(max_length=100, help_text="Un nombre descriptivo para identificar este QR (ej: 'QR Banco BCP')")
    imagen = models.ImageField(upload_to='pagos/qr_predefinidos/', 
                             verbose_name="Imagen del código QR")
    instrucciones = models.TextField(
        help_text="Instrucciones que se mostrarán al usuario para realizar el pago con este QR")
    banco = models.CharField(max_length=100, help_text="Nombre del banco o entidad asociada al QR")
    cuenta = models.CharField(max_length=100, blank=True, null=True, 
                            help_text="Número de cuenta asociada (opcional)")
    titular = models.CharField(max_length=150, 
                             help_text="Nombre del titular de la cuenta")
    activo = models.BooleanField(default=True, 
                               help_text="Desmarcar para deshabilitar este QR sin eliminarlo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.banco}"
    
    class Meta:
        verbose_name = "QR Predefinido"
        verbose_name_plural = "QRs Predefinidos"
        ordering = ['nombre']
