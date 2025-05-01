from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import DireccionEnvio, MetodoEnvio, Pedido, ItemPedido, SeguimientoPedido, Pago, QRPredefinido
from .services.whatsapp_service import WhatsAppNotificationService

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio', 'subtotal')
    can_delete = False
    max_num = 0  # No permitir añadir nuevos items desde el admin

class PagoInline(admin.StackedInline):
    model = Pago
    extra = 0
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'mostrar_qr', 'mostrar_comprobante')
    can_delete = False  # No permitir eliminar el pago desde el admin
    
    fieldsets = (
        ('Información del Pago', {
            'fields': ('estado', 'metodo_pago', 'monto', 'fecha_creacion', 'fecha_actualizacion')
        }),
        ('Detalles del Pago', {
            'fields': ('referencia', 'id_transaccion', 'token_transaccion')
        }),
        ('Comprobante de Pago', {
            'fields': ('comprobante', 'mostrar_comprobante')
        }),
        ('Pago con QR', {
            'fields': ('qr_imagen', 'mostrar_qr', 'qr_instrucciones'),
        }),
    )

    def mostrar_qr(self, obj):
        if obj.qr_imagen:
            return format_html('<img src="{}" width="150" height="150" />', obj.qr_imagen.url)
        return "No hay imagen QR"
    mostrar_qr.short_description = 'Vista previa QR'

    def mostrar_comprobante(self, obj):
        if obj.comprobante:
            return format_html('<img src="{}" width="200" />', obj.comprobante.url)
        return "No hay comprobante"
    mostrar_comprobante.short_description = 'Vista previa comprobante'

@admin.register(DireccionEnvio)
class DireccionEnvioAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'usuario', 'ciudad', 'departamento', 'es_predeterminada')
    list_filter = ('es_predeterminada', 'ciudad', 'departamento')
    search_fields = ('nombre_completo', 'usuario__username', 'direccion')

@admin.register(MetodoEnvio)
class MetodoEnvioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'tiempo_estimado', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'estado', 'total', 'fecha_pedido', 'ultimo_seguimiento', 'whatsapp_status')
    list_filter = ('estado', 'metodo_pago', 'fecha_pedido')
    search_fields = ('id', 'usuario__username', 'usuario__email', 'direccion_envio__nombre_completo')
    readonly_fields = ('subtotal', 'total', 'costo_envio', 'fecha_pedido', 'fecha_actualizacion', 'historial_seguimiento')
    inlines = [ItemPedidoInline, PagoInline]
    actions = ['marcar_como_pagado', 'marcar_como_enviado', 'marcar_como_entregado']
    change_form_template = 'admin/pedidos/pedido_change_form.html'
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('estado', 'fecha_pedido', 'fecha_actualizacion')
        }),
        ('Cliente', {
            'fields': ('usuario', 'direccion_envio')
        }),
        ('Método de Envío y Pago', {
            'fields': ('metodo_envio', 'metodo_pago', 'referencia_pago')
        }),
        ('Totales', {
            'fields': ('subtotal', 'costo_envio', 'total')
        }),
        ('Historial de seguimiento', {
            'fields': ('historial_seguimiento',),
        }),
        ('Información Adicional', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )

    def ultimo_seguimiento(self, obj):
        """Muestra el último estado de seguimiento del pedido"""
        seguimiento = obj.seguimientos.order_by('-fecha').first()
        if seguimiento:
            return seguimiento.get_estado_display()
        return "-"
    ultimo_seguimiento.short_description = 'Último seguimiento'

    def whatsapp_status(self, obj):
        """Muestra si se ha enviado notificación por WhatsApp"""
        seguimiento = obj.seguimientos.order_by('-fecha').first()
        if seguimiento and seguimiento.whatsapp_sent:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    whatsapp_status.short_description = 'WhatsApp'

    def historial_seguimiento(self, obj):
        """Muestra un historial de seguimientos en formato HTML"""
        seguimientos = obj.seguimientos.all().order_by('-fecha')
        if not seguimientos:
            return "No hay seguimientos registrados."
        
        html = '<div style="max-height: 300px; overflow-y: auto;">'
        html += '<table style="width:100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f2f2f2;"><th style="padding: 8px; text-align: left;">Fecha</th><th style="padding: 8px; text-align: left;">Estado</th><th style="padding: 8px; text-align: left;">Descripción</th><th style="padding: 8px; text-align: center;">WhatsApp</th></tr>'
        
        for s in seguimientos:
            whatsapp_icon = '✓' if s.whatsapp_sent else '✗'
            whatsapp_color = 'green' if s.whatsapp_sent else 'red'
            
            html += f'<tr style="border-bottom: 1px solid #ddd;">'
            html += f'<td style="padding: 8px;">{s.fecha.strftime("%d/%m/%Y %H:%M")}</td>'
            html += f'<td style="padding: 8px;">{s.get_estado_display()}</td>'
            html += f'<td style="padding: 8px;">{s.descripcion}</td>'
            html += f'<td style="padding: 8px; text-align: center;"><span style="color: {whatsapp_color};">{whatsapp_icon}</span></td>'
            html += '</tr>'
        
        html += '</table></div>'
        return format_html(html)
    historial_seguimiento.short_description = 'Historial de seguimiento'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/cambiar-estado/<str:estado>/',
                self.admin_site.admin_view(self.change_estado_view),
                name='pedido-cambiar-estado',
            ),
            path(
                '<path:object_id>/enviar-whatsapp/',
                self.admin_site.admin_view(self.send_whatsapp_view),
                name='pedido-enviar-whatsapp',
            ),
            path(
                '<path:object_id>/agregar-seguimiento/',
                self.admin_site.admin_view(self.add_seguimiento_view),
                name='pedido-agregar-seguimiento',
            ),
        ]
        return custom_urls + urls

    def change_estado_view(self, request, object_id, estado):
        """Vista personalizada para cambiar el estado del pedido desde un botón"""
        pedido = self.get_object(request, object_id)
        
        if pedido.estado == estado:
            self.message_user(request, f"El pedido ya está en estado '{dict(Pedido.ESTADO_CHOICES)[estado]}'", level=messages.WARNING)
            return HttpResponseRedirect(reverse('admin:pedidos_pedido_change', args=[object_id]))
        
        # Actualizar el estado del pedido
        pedido.estado = estado
        
        # Si el estado es 'pagado', actualizar también el pago asociado
        if estado == 'pagado':
            try:
                pago = Pago.objects.get(pedido=pedido)
                if pago.estado != 'completado':
                    pago.estado = 'completado'
                    pago.save()
            except Pago.DoesNotExist:
                self.message_user(request, "Advertencia: No hay un pago asociado a este pedido", level=messages.WARNING)
        
        pedido.save()
        
        self.message_user(request, f"Estado del pedido cambiado a '{dict(Pedido.ESTADO_CHOICES)[estado]}'")
        return HttpResponseRedirect(reverse('admin:pedidos_pedido_change', args=[object_id]))

    def send_whatsapp_view(self, request, object_id):
        """Vista personalizada para enviar una notificación de WhatsApp"""
        pedido = self.get_object(request, object_id)
        
        # Determinar qué tipo de notificación enviar según el estado
        if pedido.estado == 'pagado':
            result = WhatsAppNotificationService.send_payment_confirmation(pedido)
            mensaje = "Notificación de pago confirmado"
        elif pedido.estado == 'enviado':
            result = WhatsAppNotificationService.send_shipping_notification(pedido)
            mensaje = "Notificación de envío"
        else:
            self.message_user(request, "Solo se pueden enviar notificaciones para pedidos pagados o enviados", level=messages.WARNING)
            return HttpResponseRedirect(reverse('admin:pedidos_pedido_change', args=[object_id]))
        
        # Actualizar el último seguimiento para indicar que se envió WhatsApp
        ultimo_seguimiento = pedido.seguimientos.order_by('-fecha').first()
        if ultimo_seguimiento:
            ultimo_seguimiento.whatsapp_sent = True
            ultimo_seguimiento.whatsapp_notification_url = result if isinstance(result, str) else None
            ultimo_seguimiento.save()
            
            self.message_user(request, f"{mensaje} enviada por WhatsApp")
        else:
            self.message_user(request, "No hay seguimientos para este pedido", level=messages.ERROR)
            
        return HttpResponseRedirect(reverse('admin:pedidos_pedido_change', args=[object_id]))

    def add_seguimiento_view(self, request, object_id):
        """Vista para agregar un seguimiento manualmente desde el administrador"""
        if request.method != 'POST':
            return HttpResponseRedirect(reverse('admin:pedidos_pedido_change', args=[object_id]))
        
        pedido = self.get_object(request, object_id)
        estado = request.POST.get('estado')
        descripcion = request.POST.get('descripcion', '').strip()
        enviar_whatsapp = request.POST.get('enviar_whatsapp') == 'on'
        
        if not descripcion:
            self.message_user(request, "La descripción del seguimiento es obligatoria", level=messages.ERROR)
            return HttpResponseRedirect(reverse('admin:pedidos_pedido_change', args=[object_id]))
        
        # Crear el seguimiento
        seguimiento = SeguimientoPedido.objects.create(
            pedido=pedido,
            estado=estado,
            descripcion=descripcion
        )
        
        # Actualizar estado del pedido si es diferente
        if pedido.estado != estado:
            pedido.estado = estado
            pedido.save()
            
            # Si el estado es 'pagado', actualizar también el pago asociado
            if estado == 'pagado':
                try:
                    pago = Pago.objects.get(pedido=pedido)
                    if pago.estado != 'completado':
                        pago.estado = 'completado'
                        pago.save()
                except Pago.DoesNotExist:
                    pass
        
        # Enviar notificación WhatsApp si se ha seleccionado
        if enviar_whatsapp:
            result = None
            if estado == 'pagado':
                result = WhatsAppNotificationService.send_payment_confirmation(pedido)
            elif estado == 'enviado':
                result = WhatsAppNotificationService.send_shipping_notification(pedido)
            elif estado == 'en_preparacion':
                result = WhatsAppNotificationService.send_preparation_notification(pedido)
                
            if result:
                seguimiento.whatsapp_sent = True
                seguimiento.whatsapp_notification_url = result if isinstance(result, str) else None
                seguimiento.save()
                self.message_user(request, f"Notificación WhatsApp enviada correctamente")
        
        self.message_user(request, f"Seguimiento agregado correctamente")
        return HttpResponseRedirect(reverse('admin:pedidos_pedido_change', args=[object_id]))

    def marcar_como_pagado(self, request, queryset):
        """Acción masiva para marcar pedidos como pagados"""
        count = 0
        for pedido in queryset.filter(estado='pendiente'):
            pedido.estado = 'pagado'
            pedido.save()
            
            # Actualizar el pago asociado
            try:
                pago = Pago.objects.get(pedido=pedido)
                if pago.estado != 'completado':
                    pago.estado = 'completado'
                    pago.save()
            except Pago.DoesNotExist:
                pass
                
            count += 1
            
        if count:
            self.message_user(request, f"{count} pedidos marcados como pagados")
        else:
            self.message_user(request, "No se actualizó ningún pedido", level=messages.WARNING)
    marcar_como_pagado.short_description = "Marcar como pagados"
    
    def marcar_como_enviado(self, request, queryset):
        """Acción masiva para marcar pedidos como enviados"""
        count = 0
        for pedido in queryset.filter(estado__in=['pagado', 'en_preparacion']):
            pedido.estado = 'enviado'
            pedido.save()
            count += 1
            
        if count:
            self.message_user(request, f"{count} pedidos marcados como enviados")
        else:
            self.message_user(request, "No se actualizó ningún pedido", level=messages.WARNING)
    marcar_como_enviado.short_description = "Marcar como enviados"
    
    def marcar_como_entregado(self, request, queryset):
        """Acción masiva para marcar pedidos como entregados"""
        count = 0
        for pedido in queryset.filter(estado='enviado'):
            pedido.estado = 'entregado'
            pedido.save()
            count += 1
            
        if count:
            self.message_user(request, f"{count} pedidos marcados como entregados")
        else:
            self.message_user(request, "No se actualizó ningún pedido", level=messages.WARNING)
    marcar_como_entregado.short_description = "Marcar como entregados"

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido_link', 'metodo_pago', 'estado', 'monto', 'fecha_creacion', 'ver_comprobante', 'ver_qr')
    list_filter = ('estado', 'metodo_pago', 'fecha_creacion')
    search_fields = ('pedido__id', 'pedido__usuario__username', 'referencia')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'mostrar_qr', 'mostrar_comprobante')
    actions = ['marcar_como_completado']

    def pedido_link(self, obj):
        if obj.pedido:
            link = reverse("admin:pedidos_pedido_change", args=[obj.pedido.id])
            return format_html('<a href="{}">Pedido #{}</a>', link, obj.pedido.id)
        return "N/A"
    pedido_link.short_description = 'Pedido'

    def mostrar_qr(self, obj):
        if obj.qr_imagen:
            return format_html('<img src="{}" width="150" height="150" />', obj.qr_imagen.url)
        return "No hay imagen QR"
    mostrar_qr.short_description = 'Vista previa QR'

    def mostrar_comprobante(self, obj):
        if obj.comprobante:
            return format_html('<img src="{}" width="200" />', obj.comprobante.url)
        return "No hay comprobante"
    mostrar_comprobante.short_description = 'Vista previa comprobante'

    def ver_comprobante(self, obj):
        if obj.comprobante:
            return format_html('<a href="{}" target="_blank">Ver</a>', obj.comprobante.url)
        return "-"
    ver_comprobante.short_description = 'Comprobante'

    def ver_qr(self, obj):
        if obj.qr_imagen:
            return format_html('<a href="{}" target="_blank">Ver QR</a>', obj.qr_imagen.url)
        return "-"
    ver_qr.short_description = 'QR'

    def marcar_como_completado(self, request, queryset):
        """Marcar pagos como completados y actualizar los pedidos asociados"""
        count_pagos = 0
        count_pedidos = 0
        
        for pago in queryset.filter(estado__in=['pendiente', 'procesando']):
            pago.estado = 'completado'
            pago.save()
            count_pagos += 1
            
            # Actualizar el pedido asociado si existe
            if pago.pedido and pago.pedido.estado == 'pendiente':
                pago.pedido.estado = 'pagado'
                pago.pedido.save()
                count_pedidos += 1
                
        if count_pagos:
            self.message_user(request, f"{count_pagos} pagos marcados como completados. {count_pedidos} pedidos actualizados.")
        else:
            self.message_user(request, "No se actualizó ningún pago", level=messages.WARNING)
    marcar_como_completado.short_description = "Marcar como completados"

@admin.register(QRPredefinido)
class QRPredefinidoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'banco', 'titular', 'activo', 'ver_qr')
    list_filter = ('activo', 'banco')
    search_fields = ('nombre', 'banco', 'titular')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'mostrar_qr')
    
    def mostrar_qr(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="200" height="200" />', obj.imagen.url)
        return "No hay imagen QR"
    mostrar_qr.short_description = 'Vista previa QR'
    
    def ver_qr(self, obj):
        if obj.imagen:
            return format_html('<a href="{}" target="_blank">Ver QR</a>', obj.imagen.url)
        return "-"
    ver_qr.short_description = 'QR'
