from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from store.models import Product
from .models import Cart, CartItem
from .utils import get_or_create_cart
import json


def cart_view(request):
    """Страница корзины"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').prefetch_related('product__images')
    
    subtotal = cart.total_price
    delivery_cost = 300 if cart.total_items > 0 else 0
    if subtotal >= 10000:
        delivery_cost = 0
    
    # Применение промокода
    promo_code = request.session.get('promo_code')
    discount = 0
    if promo_code:
        # Логика промокода будет в отдельном приложении
        pass
    
    total = subtotal + delivery_cost - discount
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_cost': delivery_cost,
        'discount': discount,
        'total': total,
        'current_promo_code': promo_code,
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def add_to_cart(request):
    """Добавление товара в корзину"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        if quantity > product.stock:
            return JsonResponse({
                'success': False,
                'message': 'Недостаточно товара на складе'
            })
        
        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'message': 'Недостаточно товара на складе'
                })
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items,
            'message': 'Товар добавлен в корзину'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка'
        })


@require_POST
def update_cart(request):
    """Обновление количества товара в корзине"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        
        if quantity <= 0:
            cart_item.delete()
        else:
            if quantity > cart_item.product.stock:
                return JsonResponse({
                    'success': False,
                    'message': 'Недостаточно товара на складе'
                })
            cart_item.quantity = quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка'
        })


@require_POST
def remove_from_cart(request):
    """Удаление товара из корзины"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка'
        })
