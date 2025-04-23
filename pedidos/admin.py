from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse # Necesario para pedido_link
from .models import DireccionEnvio, MetodoEnvio, Pedido, ItemPedido, SeguimientoPedido, Pago, QRPredefinido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio', 'subtotal')
    can_delete = False

class SeguimientoPedidoInline(admin.TabularInline):
    model = SeguimientoPedido
    extra = 1 # Permitir añadir uno nuevo fácilmente
    fields = ('estado', 'descripcion', 'fecha')
    ordering = ('-fecha',) # Ordenar por fecha descendente

class PagoInline(admin.StackedInline):
    model = Pago
    extra = 0 # No mostrar formularios extra para añadir pagos desde aquí
    readonly_fields = ('monto', 'metodo_pago', 'fecha_creacion', 'estado', 'referencia', 'id_transaccion', 'comprobante', 'qr_imagen')
    fields = ('estado', 'monto', 'metodo_pago', 'referencia', 'fecha_creacion') # Campos a mostrar
    can_delete = False # Evitar borrar el pago desde el pedido

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
    list_display = ('id', 'usuario', 'estado', 'pago_asociado_estado', 'total', 'fecha_pedido')
    list_filter = ('estado', 'metodo_pago', 'fecha_pedido') # Añadido metodo_pago
    search_fields = ('id', 'usuario__username', 'usuario__email', 'direccion_envio__nombre_completo') # Añadido direccion
    readonly_fields = ('subtotal', 'total', 'costo_envio', 'fecha_pedido', 'fecha_actualizacion')
    inlines = [ItemPedidoInline, SeguimientoPedidoInline, PagoInline]
    actions = ['marcar_como_pagado'] # Añadir la acción personalizada
    
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
        ('Información Adicional', {
            'fields': ('notas',),
            'classes': ('collapse',) # Mantener colapsado por defecto
        }),
    )

    def pago_asociado_estado(self, obj):
        try:
            pago = Pago.objects.get(pedido=obj) # Forma más directa si es OneToOne o ForeignKey único
            return pago.get_estado_display()
        except Pago.DoesNotExist:
            return "Sin pago"
        except Pago.MultipleObjectsReturned: # Si por error hay más de un pago
             return "Múltiples pagos"
        except AttributeError: # Si la relación inversa no está definida como se espera
            return "Error relación"

    pago_asociado_estado.short_description = 'Estado Pago' # Nombre corto para la columna

    def save_model(self, request, obj, form, change):
        estado_anterior = None
        if change and 'estado' in form.initial: # Si es una modificación y el campo estado estaba en el form inicial
             estado_anterior = form.initial['estado']

        # IMPORTANTE: Al guardar el modelo, el método save() del modelo ya creará automáticamente 
        # un registro de seguimiento, así que no necesitamos duplicar esa lógica aquí
        super().save_model(request, obj, form, change)

        # Solo manejar el caso específico del estado pagado para la actualización del Pago
        if obj.estado == 'pagado' and estado_anterior != 'pagado':
            try:
                pago = Pago.objects.get(pedido=obj)
                if pago.estado in ['pendiente', 'procesando']:
                    pago.estado = 'completado'
                    pago.save()
                    self.message_user(request, f"El estado del Pago asociado al Pedido #{obj.id} se actualizó automáticamente a 'Completado'.")
            except Pago.DoesNotExist:
                self.message_user(request, f"Advertencia: El Pedido #{obj.id} se marcó como pagado, pero no se encontró un Pago asociado para actualizar.", level='warning')
            except Pago.MultipleObjectsReturned:
                 self.message_user(request, f"Error: Hay múltiples Pagos asociados al Pedido #{obj.id}. No se actualizó automáticamente.", level='error')
            except Exception as e:
                 self.message_user(request, f"Error inesperado al actualizar el pago asociado para Pedido #{obj.id}: {e}", level='error')

    def marcar_como_pagado(self, request, queryset):
        pedidos_actualizados = 0
        pagos_actualizados = 0
        for pedido in queryset.filter(estado='pendiente'): # Solo actuar sobre pendientes
            pedido.estado = 'pagado'
            pedido.save() # Guardar para disparar save_model si es necesario (o replicar lógica aquí)
            pedidos_actualizados += 1
            try:
                pago = Pago.objects.get(pedido=pedido)
                if pago.estado in ['pendiente', 'procesando']:
                    pago.estado = 'completado'
                    pago.save()
                    pagos_actualizados += 1
                    if not SeguimientoPedido.objects.filter(pedido=pedido, estado='pagado').exists():
                        SeguimientoPedido.objects.create(
                            pedido=pedido, estado='pagado', descripcion='Pago confirmado por acción masiva admin.'
                        )
            except Pago.DoesNotExist:
                 self.message_user(request, f"Advertencia: Pedido #{pedido.id} marcado como pagado, pero sin Pago asociado.", level='warning')
            except Pago.MultipleObjectsReturned:
                 self.message_user(request, f"Error: Múltiples Pagos para Pedido #{pedido.id}.", level='error')
            except Exception as e:
                 self.message_user(request, f"Error al actualizar pago para Pedido #{pedido.id}: {e}", level='error')

        if pedidos_actualizados > 0:
            self.message_user(request, f"{pedidos_actualizados} pedidos marcados como 'pagado'. {pagos_actualizados} pagos asociados actualizados a 'completado'.")
        else:
            self.message_user(request, "No se seleccionaron pedidos pendientes para actualizar.", level='warning')

    marcar_como_pagado.short_description = "Marcar seleccionados como Pagado (y completar pago)"

@admin.register(SeguimientoPedido)
class SeguimientoPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'estado', 'fecha', 'descripcion_corta') # Añadido descripcion_corta
    list_filter = ('estado', 'fecha')
    search_fields = ('pedido__id', 'descripcion')
    readonly_fields = ('fecha',) # Fecha se establece automáticamente

    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido_link', 'metodo_pago', 'estado', 'monto', 'fecha_creacion', 'ver_comprobante', 'ver_qr')
    list_filter = ('estado', 'metodo_pago', 'fecha_creacion')
    search_fields = ('pedido__id', 'pedido__usuario__username', 'referencia')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'mostrar_qr', 'mostrar_comprobante')

    fieldsets = (
        ('Información del Pago', {
            'fields': ('estado', 'metodo_pago', 'monto', 'fecha_creacion', 'fecha_actualizacion')
        }),
        ('Pedido Relacionado', {
            'fields': ('pedido',)
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
        ('Datos API', {
            'fields': ('api_callback_url', 'api_webhook_recibido', 'datos_adicionales'),
            'classes': ('collapse',)
        }),
    )

    def pedido_link(self, obj):
        if obj.pedido:
            link = reverse("admin:pedidos_pedido_change", args=[obj.pedido.id])
            return format_html('<a href="{}">Pedido #{}</a>', link, obj.pedido.id)
        return "N/A"
    pedido_link.short_description = 'Pedido' # Nombre de la columna

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

    actions = ['marcar_como_completado', 'marcar_como_pendiente']

    def marcar_como_completado(self, request, queryset):
        updated_count = 0
        for pago in queryset.filter(estado__in=['pendiente', 'procesando']):
            pago.estado = 'completado'
            pago.save()
            updated_count += 1
            if pago.pedido and pago.pedido.estado == 'pendiente':
                 pago.pedido.estado = 'pagado'
                 pago.pedido.save()
                 if not SeguimientoPedido.objects.filter(pedido=pago.pedido, estado='pagado').exists():
                     SeguimientoPedido.objects.create(
                         pedido=pago.pedido, estado='pagado', descripcion='Pago confirmado por acción masiva en Pagos.'
                     )

        if updated_count > 0:
            self.message_user(request, f"Se han marcado {updated_count} pagos como completados.")
        else:
             self.message_user(request, "No se seleccionaron pagos pendientes o procesando para actualizar.", level='warning')
    marcar_como_completado.short_description = "Marcar pagos seleccionados como completados"

    def marcar_como_pendiente(self, request, queryset):
        updated_count = queryset.update(estado='pendiente')
        self.message_user(request, f"Se han marcado {updated_count} pagos como pendientes")
    marcar_como_pendiente.short_description = "Marcar pagos seleccionados como pendientes"

@admin.register(QRPredefinido)
class QRPredefinidoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'banco', 'titular', 'activo', 'ver_qr')
    list_filter = ('activo', 'banco')
    search_fields = ('nombre', 'banco', 'titular')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'mostrar_qr')
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'activo', 'banco', 'titular', 'cuenta')
        }),
        ('Código QR', {
            'fields': ('imagen', 'mostrar_qr', 'instrucciones')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
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
