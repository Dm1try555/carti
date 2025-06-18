from .utils import get_cart_items_count


def cart_context(request):
    """Контекстный процессор для корзины"""
    return {
        'cart_items_count': get_cart_items_count(request),
    }


from .models import Category

def categories_processor(request):
    return {
        'categories': Category.objects.filter(is_active=True)
    }

