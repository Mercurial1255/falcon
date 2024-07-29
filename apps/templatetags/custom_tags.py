from django.template import Library

from apps.models import Favourite

register = Library()


@register.filter()
def str_to_phone(value, arg=None):
    if value.startswith('+998'):
        return value
    return f"+998{value}"


@register.filter()
def is_liked(user, product) -> bool:
    return Favourite.objects.filter(user=user, product=product).exists()
