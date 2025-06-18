from django.contrib import admin
from .models import Order, OrderItem


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
        ('Інформація о замовленні', {
            'fields': ('order_number', 'status', 'created_at', 'updated_at')
        }),
        ('Інформація про клієнта', {
            'fields': ('first_name', 'last_name', 'phone', 'email')
        }),
        ('Доставка', {
            'fields': ('delivery_method', 'city', 'address', 'postal_code', 'delivery_time')
        }),
        ('Оплата', {
            'fields': ('payment_method', 'is_paid')
        }),
        ('Суми', {
            'fields': ('subtotal', 'delivery_cost', 'discount', 'total')
        }),
        ('Додатково', {
            'fields': ('notes',)
        }),
    )
