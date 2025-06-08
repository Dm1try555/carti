from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:catalog') + f'?category={self.slug}'


class Product(models.Model):
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория', related_name='products')
    description = models.TextField('Краткое описание')
    full_description = models.TextField('Полное описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    discount_price = models.DecimalField('Цена со скидкой', max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField('Количество на складе', default=0)
    
    # Product options stored as JSON
    colors = models.JSONField('Доступные цвета', default=list, blank=True)
    sizes = models.JSONField('Доступные размеры', default=list, blank=True)
    
    # Product features and specifications
    features = models.JSONField('Особенности', default=list, blank=True)
    specifications = models.JSONField('Характеристики', default=dict, blank=True)
    care_instructions = models.TextField('Инструкции по уходу', blank=True)
    
    # Status flags
    is_active = models.BooleanField('Активен', default=True)
    is_featured = models.BooleanField('Рекомендуемый', default=False)
    is_new = models.BooleanField('Новинка', default=False)
    
    # SEO fields
    meta_title = models.CharField('Meta Title', max_length=200, blank=True)
    meta_description = models.TextField('Meta Description', blank=True)
    
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
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
    image = models.ImageField('Изображение', upload_to='products/')
    alt_text = models.CharField('Alt текст', max_length=200, blank=True)
    is_main = models.BooleanField('Главное изображение', default=False)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.product.name} - Изображение {self.id}'

    def save(self, *args, **kwargs):
        if self.is_main:
            # Ensure only one main image per product
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class Cart(models.Model):
    session_key = models.CharField('Ключ сессии', max_length=40)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', blank=True, null=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'Корзина {self.id}'

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Корзина')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество', default=1)
    selected_options = models.JSONField('Выбранные опции', default=dict, blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    @property
    def total_price(self):
        return self.product.final_price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('confirmed', 'Подтвержден'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Наличными при получении'),
        ('card', 'Картой при получении'),
        ('online', 'Онлайн оплата'),
    ]

    DELIVERY_CHOICES = [
        ('courier', 'Курьерская доставка'),
        ('pickup', 'Самовывоз'),
    ]

    # Order info
    order_number = models.CharField('Номер заказа', max_length=20, unique=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Customer info
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email', blank=True)
    
    # Delivery info
    delivery_method = models.CharField('Способ доставки', max_length=20, choices=DELIVERY_CHOICES)
    city = models.CharField('Город', max_length=100)
    address = models.TextField('Адрес доставки', blank=True)
    postal_code = models.CharField('Индекс', max_length=10, blank=True)
    delivery_time = models.CharField('Время доставки', max_length=20, blank=True)
    
    # Payment info
    payment_method = models.CharField('Способ оплаты', max_length=20, choices=PAYMENT_CHOICES)
    is_paid = models.BooleanField('Оплачен', default=False)
    
    # Order totals
    subtotal = models.DecimalField('Сумма товаров', max_digits=10, decimal_places=2)
    delivery_cost = models.DecimalField('Стоимость доставки', max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField('Скидка', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('Итого', max_digits=10, decimal_places=2)
    
    # Additional info
    notes = models.TextField('Комментарий к заказу', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.order_number}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        import random
        import string
        return ''.join(random.choices(string.digits, k=8))

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    product_name = models.CharField('Название товара', max_length=200)
    product_price = models.DecimalField('Цена товара', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество')
    selected_options = models.JSONField('Выбранные опции', default=dict, blank=True)
    total_price = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'


class PromoCode(models.Model):
    code = models.CharField('Код', max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField('Процент скидки', validators=[MinValueValidator(1), MaxValueValidator(100)])
    min_order_amount = models.DecimalField('Минимальная сумма заказа', max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField('Максимальное количество использований', blank=True, null=True)
    used_count = models.PositiveIntegerField('Количество использований', default=0)
    is_active = models.BooleanField('Активен', default=True)
    valid_from = models.DateTimeField('Действует с')
    valid_until = models.DateTimeField('Действует до')
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'

    def __str__(self):
        return self.code

    def is_valid(self, order_amount=0):
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False, 'Промокод неактивен'
        
        if now < self.valid_from or now > self.valid_until:
            return False, 'Промокод истек'
        
        if self.max_uses and self.used_count >= self.max_uses:
            return False, 'Промокод исчерпан'
        
        if order_amount < self.min_order_amount:
            return False, f'Минимальная сумма заказа {self.min_order_amount} ₽'
        
        return True, 'Промокод действителен'


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('order', 'Вопрос по заказу'),
        ('product', 'Вопрос о товаре'),
        ('custom', 'Индивидуальный заказ'),
        ('complaint', 'Жалоба'),
        ('other', 'Другое'),
    ]

    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    subject = models.CharField('Тема', max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField('Сообщение')
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.get_subject_display()}'
