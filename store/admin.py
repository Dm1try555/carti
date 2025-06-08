from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Product, ProductImage, Cart, CartItem, 
    Order, OrderItem, PromoCode, ContactMessage
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'products_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Количество товаров'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_main', 'order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_active', 'is_featured', 'created_at']
    list_filter = ['category', 'is_active', 'is_featured', 'is_new', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category', 'description', 'full_description')
        }),
        ('Цены и склад', {
            'fields': ('price', 'discount_price', 'stock')
        }),
        ('Опции товара', {
            'fields': ('colors', 'sizes', 'features', 'specifications', 'care_instructions'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('is_active', 'is_featured', 'is_new')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']
    inlines = [CartItemInline]
    readonly_fields = ['total_items', 'total_price']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'status', 'payment_method', 'total', 'created_at']
    list_filter = ['status', 'payment_method', 'delivery_method', 'is_paid', 'created_at']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('order_number', 'status', 'created_at', 'updated_at')
        }),
        ('Информация о клиенте', {
            'fields': ('first_name', 'last_name', 'phone', 'email')
        }),
        ('Доставка', {
            'fields': ('delivery_method', 'city', 'address', 'postal_code', 'delivery_time')
        }),
        ('Оплата', {
            'fields': ('payment_method', 'is_paid')
        }),
        ('Суммы', {
            'fields': ('subtotal', 'delivery_cost', 'discount', 'total')
        }),
        ('Дополнительно', {
            'fields': ('notes',)
        }),
    )


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'min_order_amount', 'used_count', 'max_uses', 'is_active', 'valid_until']
    list_filter = ['is_active', 'valid_from', 'valid_until']
    search_fields = ['code']
    readonly_fields = ['used_count', 'created_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['subject', 'is_read', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = 'Отметить как прочитанное'
    
    actions = ['mark_as_read']
