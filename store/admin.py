from django.contrib import admin
from django.utils.text import slugify
from .models import Category, Product, ProductImage
from .forms import ProductAdminForm


@admin.action(description='Дублікувати вибрані товари')
def duplicate_products(modeladmin, request, queryset):
    for product in queryset:
        product.pk = None  # Сбросить pk — чтобы создать новый объект
        product.slug = ''  # Оставить пустым, чтобы админка сгенерировала slug
        product.save()



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'products_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Кількість товарів'

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_main', 'order']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_active', 'is_featured', 'created_at']
    list_filter = ['category', 'is_active', 'is_featured', 'is_new', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    actions = [duplicate_products]
    
    fieldsets = (
        ('Загальна інформація', {
            'fields': ('name', 'slug', 'category', 'description', 'full_description')
        }),
        ('Ціна та кількість', {
            'fields': ('price', 'discount_price', 'stock')
        }),
        ('Опції товару', {
            'fields': ('colors', 'sizes', 'features', 'care_instructions'),
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
