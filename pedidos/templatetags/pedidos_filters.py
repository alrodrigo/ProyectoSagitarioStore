from django.template import Library

register = Library()

@register.filter
def get_item(dictionary, key):
    """
    Obtiene un elemento de un diccionario usando una clave.
    Útil para acceder a diccionarios en plantillas.
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def sub(value, arg):
    """
    Resta el argumento del valor.
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value