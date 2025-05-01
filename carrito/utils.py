from django.core.cache import cache
from django.conf import settings

def get_cached_product(product_id):
    cache_key = f'product_{product_id}'
    product = cache.get(cache_key)
    if product is None:
        try:
            from productos.models import Product
            product = Product.objects.get(id=product_id)
            cache.set(cache_key, product, timeout=3600)  # Cache por 1 hora
        except Product.DoesNotExist:
            return None
    return product

def calculate_cart_totals(cart_items):
    """
    Calcula los totales del carrito de manera eficiente
    """
    subtotal = sum(item['producto'].price * item['cantidad'] for item in cart_items)
    iva = subtotal * settings.IVA_RATE if hasattr(settings, 'IVA_RATE') else 0
    total = subtotal + iva
    return {
        'subtotal': subtotal,
        'iva': iva,
        'total': total
    }

def format_currency(amount):
    """
    Formatea cantidades monetarias de manera consistente
    """
    return f"${amount:,.2f}"