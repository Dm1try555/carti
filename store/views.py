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

from contact.models import ContactMessage

from .models import Category, Product
from cart.models import Cart, CartItem
from promo.models import PromoCode
from checkout.models import Order, OrderItem

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


def about(request):
    """Страница о компании"""
    return render(request, 'store/about.html')



