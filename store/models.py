from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField('Назва категорії', max_length=100)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Опис', blank=True)
    image = models.ImageField('Зображення', upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Створено', auto_now_add=True)

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:catalog') + f'?category={self.slug}'


class Product(models.Model):
    name = models.CharField('Назва товару', max_length=200)
    slug = models.SlugField('URL', unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категорія', related_name='products')
    description = models.TextField('Короткий опис', blank=True)
    full_description = models.TextField('Повний опис', blank=True)
    price = models.DecimalField('Ціна', max_digits=10, decimal_places=2)
    discount_price = models.DecimalField('Ціна зі знижкою', max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField('Кількість на складі', default=0)
    
    # Product options stored as JSON
    colors = models.JSONField('Доступні кольори', default=list, blank=True, null=True)
    sizes = models.JSONField('Доступні розміри', default=list, blank=True, null=True)
    
    # Product features and specifications
    features = models.JSONField('Особливості', default=list, blank=True, null=True)
    specifications = models.JSONField('Характеристики', default=dict, blank=True, null=True)
    care_instructions = models.TextField('Інструкції по догляду', blank=True, null=True)
    
    # Status flags
    is_active = models.BooleanField('Активний', default=True)
    is_featured = models.BooleanField('Рекомендований', default=False)
    is_new = models.BooleanField('Новинка', default=False)
    
    # SEO fields
    meta_title = models.CharField('Meta Title', max_length=200, blank=True)
    meta_description = models.TextField('Meta Description', blank=True)
    
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'id': self.id})

    @property
    def discount_percentage(self):
        if self.discount_price and self.price:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def is_in_stock(self):
        return self.stock > 0

    def get_main_image(self):
        image = self.images.first()
        return image.image if image else None


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')
    image = models.ImageField('Зображення', upload_to='products/')
    alt_text = models.CharField('Alt текст', max_length=200, blank=True)
    is_main = models.BooleanField('Головне зображення', default=False)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Зображення товару'
        verbose_name_plural = 'Зображення товарів'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.product.name} - Зображення {self.id}'

    def save(self, *args, **kwargs):
        if self.is_main:
            # Ensure only one main image per product
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)
