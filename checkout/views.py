from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from cart.utils import get_or_create_cart
from .models import Order, OrderItem


def checkout(request):
    """Страница оформления заказа"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').prefetch_related('product__images')
    
    if not cart_items:
        messages.error(request, 'Ваша корзина пуста')
        return redirect('cart:cart')
    
    subtotal = cart.total_price
    delivery_cost = 300 if subtotal < 10000 else 0
    
    # Применение промокода
    promo_code = request.session.get('promo_code')
    discount = 0
    # Логика промокода будет в отдельном приложении
    
    total = subtotal + delivery_cost - discount
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_cost': delivery_cost,
        'discount': discount,
        'total': total,
    }
    return render(request, 'checkout/checkout.html', context)


@require_POST
def process_order(request):
    """Обработка заказа"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product')
    
    if not cart_items:
        messages.error(request, 'Ваша корзина пуста')
        return redirect('cart:cart')
    
    # Создание заказа
    subtotal = cart.total_price
    delivery_cost = 300 if request.POST.get('delivery_method') == 'courier' else 0
    if subtotal >= 10000:
        delivery_cost = 0
    
    # Применение промокода
    discount = 0
    promo_code = request.session.get('promo_code')
    # Логика промокода будет в отдельном приложении
    
    total = subtotal + delivery_cost - discount
    
    order = Order.objects.create(
        first_name=request.POST.get('first_name'),
        last_name=request.POST.get('last_name'),
        phone=request.POST.get('phone'),
        email=request.POST.get('email', ''),
        delivery_method=request.POST.get('delivery_method'),
        city=request.POST.get('city', ''),
        address=request.POST.get('address', ''),
        postal_code=request.POST.get('postal_code', ''),
        delivery_time=request.POST.get('delivery_time', ''),
        payment_method=request.POST.get('payment_method'),
        subtotal=subtotal,
        delivery_cost=delivery_cost,
        discount=discount,
        total=total,
        notes=request.POST.get('notes', ''),
    )
    
    # Создание элементов заказа
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            product_name=cart_item.product.name,
            product_price=cart_item.product.final_price,
            quantity=cart_item.quantity,
            selected_options=cart_item.selected_options,
            total_price=cart_item.total_price,
        )
        
        # Уменьшение количества на складе
        cart_item.product.stock -= cart_item.quantity
        cart_item.product.save()
    
    # Очистка корзины и промокода
    cart.items.all().delete()
    if 'promo_code' in request.session:
        del request.session['promo_code']
    
    messages.success(request, f'Заказ #{order.order_number} успешно оформлен! Мы свяжемся с вами в ближайшее время.')
    return redirect('store:index')
