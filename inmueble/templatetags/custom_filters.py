from django import template

register = template.Library()

@register.filter(name='equals')
def equals(value, arg):
    """Compara si dos valores son iguales (como strings)"""
    return str(value) == str(arg)


from django import template

register = template.Library()

@register.filter
def sum_attribute(queryset, attribute):
    try:
        return sum(float(item.get(attribute, 0)) for item in queryset)
    except (TypeError, ValueError):
        return 0