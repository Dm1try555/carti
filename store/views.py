from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.conf import settings
import json

from .models import (
    Category, Product, Cart, CartItem, Order, OrderItem, 
    PromoCode, ContactMessage
)
from .utils import get_or_create_cart


def index(request):
    """Главная страница"""
    categories = Category.objects.filter(is_active=True)[:4]
    featured_products = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).select_related('category').prefetch_related('images')[:8]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'store/index.html', context)


def catalog(request):
    """Страница каталога с фильтрами"""
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    categories = Category.objects.filter(is_active=True)
    
    # Фильтрация
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        current_category = get_object_or_404(Category, slug=category_slug)
    else:
        current_category = None
    
    # Поиск
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Фильтр по цене
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    
    # Фильтр по цвету
    colors = request.GET.getlist('color')
    if colors:
        products = products.filter(colors__overlap=colors)
    
    # Сортировка
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-is_featured', '-created_at')
    
    # Пагинация
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    # Доступные цвета для фильтра
    all_colors = set()
    for product in Product.objects.filter(is_active=True):
        if product.colors:
            all_colors.update(product.colors)
    
    context = {
        'products': products_page,
        'categories': categories,
        'current_category': current_category,
        'available_colors': sorted(all_colors),
        'search_query': search_query,
    }
    return render(request, 'store/catalog.html', context)


def product_detail(request, id):
    """Детальная страница товара"""
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images'),
        id=id,
        is_active=True
    )
    
    # Похожие товары
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).prefetch_related('images')[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


def cart_view(request):
    """Страница корзины"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').prefetch_related('product__images')
    
    subtotal = cart.total_price
    delivery_cost = 300 if cart.total_items > 0 else 0  # Бесплатная доставка от 10000
    if subtotal >= 10000:
        delivery_cost = 0
    
    # Применение промокода
    promo_code = request.session.get('promo_code')
    discount = 0
    if promo_code:
        try:
            promo = PromoCode.objects.get(code=promo_code)
            is_valid, message = promo.is_valid(subtotal)
            if is_valid:
                discount = (subtotal * promo.discount_percentage) / 100
            else:
                del request.session['promo_code']
                messages.error(request, message)
        except PromoCode.DoesNotExist:
            del request.session['promo_code']
    
    total = subtotal + delivery_cost - discount
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_cost': delivery_cost,
        'discount': discount,
        'total': total,
        'current_promo_code': promo_code,
    }
    return render(request, 'cart.html', context)


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


@require_POST
def apply_promo(request):
    """Применение промокода"""
    promo_code = request.POST.get('promo_code', '').strip().upper()
    
    if not promo_code:
        messages.error(request, 'Введите промокод')
        return redirect('store:cart')
    
    try:
        promo = PromoCode.objects.get(code=promo_code)
        cart = get_or_create_cart(request)
        
        is_valid, message = promo.is_valid(cart.total_price)
        if is_valid:
            request.session['promo_code'] = promo_code
            messages.success(request, f'Промокод применен! Скидка {promo.discount_percentage}%')
        else:
            messages.error(request, message)
            
    except PromoCode.DoesNotExist:
        messages.error(request, 'Промокод не найден')
    
    return redirect('store:cart')


def checkout(request):
    """Страница оформления заказа"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').prefetch_related('product__images')
    
    if not cart_items:
        messages.error(request, 'Ваша корзина пуста')
        return redirect('store:cart')
    
    subtotal = cart.total_price
    delivery_cost = 300 if subtotal < 10000 else 0
    
    # Применение промокода
    promo_code = request.session.get('promo_code')
    discount = 0
    if promo_code:
        try:
            promo = PromoCode.objects.get(code=promo_code)
            is_valid, message = promo.is_valid(subtotal)
            if is_valid:
                discount = (subtotal * promo.discount_percentage) / 100
        except PromoCode.DoesNotExist:
            pass
    
    total = subtotal + delivery_cost - discount
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_cost': delivery_cost,
        'discount': discount,
        'total': total,
    }
    return render(request, 'checkout.html', context)


@require_POST
def process_order(request):
    """Обработка заказа"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product')
    
    if not cart_items:
        messages.error(request, 'Ваша корзина пуста')
        return redirect('store:cart')
    
    # Создание заказа
    subtotal = cart.total_price
    delivery_cost = 300 if request.POST.get('delivery_method') == 'courier' else 0
    if subtotal >= 10000:
        delivery_cost = 0
    
    # Применение промокода
    discount = 0
    promo_code = request.session.get('promo_code')
    if promo_code:
        try:
            promo = PromoCode.objects.get(code=promo_code)
            is_valid, message = promo.is_valid(subtotal)
            if is_valid:
                discount = (subtotal * promo.discount_percentage) / 100
                promo.used_count += 1
                promo.save()
        except PromoCode.DoesNotExist:
            pass
    
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


def about(request):
    """Страница о компании"""
    return render(request, 'store/about.html')


def contact(request):
    """Страница контактов"""
    return render(request, 'contact.html')


@require_POST
def send_message(request):
    """Отправка сообщения"""
    try:
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        )
        messages.success(request, 'Ваше сообщение отправлено! Мы ответим в ближайшее время.')
    except Exception as e:
        messages.error(request, 'Произошла ошибка при отправке сообщения.')
    
    return redirect('store:contact')


# Дополнительные страницы
def delivery(request):
    """Страница доставки и оплаты"""
    return render(request, 'delivery.html')


def returns(request):
    """Страница возврата и обмена"""
    return render(request, 'returns.html')


def care(request):
    """Страница ухода за изделиями"""
    return render(request, 'care.html')


def privacy(request):
    """Страница политики конфиденциальности"""
    return render(request, 'privacy.html')
