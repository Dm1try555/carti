from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, F, DecimalField
from django.utils import timezone
from django.conf import settings
import json

from contact.models import ContactMessage

from .models import Category, Product
from cart.models import Cart, CartItem
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
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    categories = Category.objects.filter(is_active=True)

    # Фільтрація за категорією
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        current_category = get_object_or_404(Category, slug=category_slug)
    else:
        current_category = None

    # Анотація для ефективної ціни
    products = products.annotate(
        effective_price=Case(
            When(discount_price__isnull=False, then=F('discount_price')),
            default=F('price'),
            output_field=DecimalField(),
        )
    )

    # Фільтр по ціні по effective_price
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        try:
            price_min_value = float(price_min)
            products = products.filter(effective_price__gte=price_min_value)
        except ValueError:
            pass
    if price_max:
        try:
            price_max_value = float(price_max)
            products = products.filter(effective_price__lte=price_max_value)
        except ValueError:
            pass

    # Фільтр по кольору
    colors = request.GET.getlist('color')
    selected_colors = colors.copy()
    if colors:
        color_filter = Q()
        for color in colors:
            color_filter |= Q(colors__contains=[color])
        products = products.filter(color_filter)

    # Сортування по effective_price, якщо сортування за ціною
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_asc':
        products = products.order_by('effective_price')
    elif sort_by == 'price_desc':
        products = products.order_by('-effective_price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-is_featured', '-created_at')

    # Пагінація
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    # Доступні кольори
    all_colors = set()
    for product in Product.objects.filter(is_active=True):
        if product.colors:
            all_colors.update(product.colors)

    context = {
        'products': products_page,
        'categories': categories,
        'current_category': current_category,
        'available_colors': sorted(all_colors),
        'selected_colors': colors,
    }
    return render(request, 'store/catalog.html', context)



def product_detail(request, id):
    """Детальна сторінка товару"""
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images'),
        id=id,
        is_active=True
    )

    # Головне фото для основного товару
    main_image = product.images.filter(is_main=True).first()

    # Похожие товары
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).prefetch_related('images')[:4]

    # (Опційно) можна підготувати головні фото для кожного related_product
    # Наприклад, у словнику:
    related_products_main_images = {
        rp.id: rp.images.filter(is_main=True).first() for rp in related_products
    }

    context = {
        'product': product,
        'main_image': main_image,
        'related_products': related_products,
        'related_products_main_images': related_products_main_images,
    }
    return render(request, 'store/product_detail.html', context)



def about(request):
    """Страница о компании"""
    return render(request, 'store/about.html')



