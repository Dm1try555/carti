from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from cart.utils import get_or_create_cart
from .models import PromoCode


@require_POST
def apply_promo(request):
    """Застосування промокоду"""
    promo_code = request.POST.get('promo_code', '').strip().upper()
    
    if not promo_code:
        messages.error(request, 'Введіть промокод')
        return redirect('cart:cart')
    
    try:
        promo = PromoCode.objects.get(code=promo_code)
        cart = get_or_create_cart(request)
        
        is_valid, message = promo.is_valid(cart.total_price)
        if is_valid:
            request.session['promo_code'] = promo_code
            messages.success(request, f'Промокод застосовано! Знижка {promo.discount_percentage}%')
        else:
            messages.error(request, message)
            
    except PromoCode.DoesNotExist:
        messages.error(request, 'Промокод не знайдено')
    
    return redirect('cart:cart')
