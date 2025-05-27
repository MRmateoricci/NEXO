from django import template

register = template.Library()

@register.filter(name='equals')
def equals(value, arg):
    """Compara si dos valores son iguales (como strings)"""
    return str(value) == str(arg)