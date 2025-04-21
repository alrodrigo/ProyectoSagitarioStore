from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('cart/', views.carrito_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.mis_pedidos_view, name='orders'),
]
