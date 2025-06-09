from django.db import models
from store.models import Product


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
