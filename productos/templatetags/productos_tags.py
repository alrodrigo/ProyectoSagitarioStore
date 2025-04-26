from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filtro para obtener un elemento de un diccionario por su clave.
    Uso en plantillas: {{ mi_dict|get_item:mi_clave }}
    """
    if dictionary is None:
        return None
    
    # Si la clave es un objeto (como un modelo), intentar usarlo directamente
    if key in dictionary:
        return dictionary[key]
    
    # Si no funciona, intentar con su id como string
    try:
        if hasattr(key, 'id'):
            key_id = str(key.id)
            if key_id in dictionary:
                return dictionary[key_id]
    except:
        pass
        
    return []  # Devolver lista vacía como valor por defecto