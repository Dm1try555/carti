from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def currency(value):
    """Форматирование цены"""
    try:
        return f"{int(value):,} ₽".replace(',', ' ')
    except (ValueError, TypeError):
        return "0 ₽"


@register.filter
def multiply(value, arg):
    """Умножение"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.simple_tag
def get_main_image(product):
    """Получение главного изображения товара"""
    main_image = product.images.filter(is_main=True).first()
    if main_image:
        return main_image.image.url
    
    first_image = product.images.first()
    if first_image:
        return first_image.image.url
    
    return '/static/images/product-placeholder.jpg'


@register.inclusion_tag('includes/product_card.html')
def product_card(product):
    """Карточка товара"""
    return {'product': product}


@register.inclusion_tag('includes/breadcrumbs.html')
def breadcrumbs(items):
    """Хлебные крошки"""
    return {'items': items}
