from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtener un item de un diccionario usando una clave"""
    if dictionary is None:
        return None
    return dictionary.get(int(key))
