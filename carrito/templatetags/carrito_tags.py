from django import template

register = template.Library()

@register.filter
def cart_total_items(carrito):
    """Devuelve el número total de productos en el carrito sumando todas las cantidades"""
    if not carrito:
        return 0
    return sum(int(cantidad) for cantidad in carrito.values())