from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    # URLs del proceso de checkout
    path('checkout/direccion/', views.checkout_paso1, name='checkout_paso1'),
    path('checkout/envio/', views.checkout_paso2, name='checkout_paso2'),
    path('checkout/confirmacion/', views.checkout_paso3, name='checkout_paso3'),
    path('checkout/completado/<int:pedido_id>/', views.confirmacion_pedido, name='confirmacion_pedido'),
    
    # URLs de gestión de pedidos
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('mis-pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    
    # URLs para gestión de direcciones
    path('direcciones/<int:direccion_id>/editar/', views.editar_direccion, name='editar_direccion'),
    path('direcciones/<int:direccion_id>/eliminar/', views.eliminar_direccion, name='eliminar_direccion'),
    
    # URLs para gestión de pagos
    path('pagos/<int:pago_id>/subir-comprobante/', views.subir_comprobante, name='subir_comprobante'),
    path('verificar-pago/<int:pedido_id>/', views.verificar_pago, name='verificar_pago'),
    
    # URLs para reservas
    path('reservas/', views.mis_reservas, name='mis_reservas'),
    path('reservas/<int:reserva_id>/', views.detalle_reserva, name='detalle_reserva'),
    path('reservas/solicitar/<int:producto_id>/', views.solicitar_reserva, name='solicitar_reserva'),
    path('reservas/<int:reserva_id>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
    path('reservas/<int:reserva_id>/anticipo/', views.registrar_anticipo_reserva, name='registrar_anticipo_reserva'),
    path('reservas/<int:reserva_id>/verificar-anticipo/', views.verificar_anticipo_reserva, name='verificar_anticipo_reserva'),
    path('reservas/<int:reserva_id>/convertir/', views.convertir_reserva, name='convertir_reserva'),
]
