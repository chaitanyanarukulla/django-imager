"""."""
from django import template


register = template.Library()

import pdb; pdb.set_trace()
@register.filter
def modulo(num, val):
    """."""
    return num % val
