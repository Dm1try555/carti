from django.db import models
from store.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує обробки'),
        ('confirmed', 'Підтверджено'),
        ('processing', 'В обробці'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Накладений платіж (з попередньою передоплатою)'),
        ('card', 'Онлайн-оплата на карту'),
    ]

    DELIVERY_CHOICES = [
        ('nova_poshta', 'Доставка Новою Поштою'),
        
    ]

    MESSENGERS_CHOICES = [
        ('empty', '---'),
        ('telegram', 'Telegram'),
        ('viber', 'Viber'),
        ('whatsapp', 'WhatsApp'),
    ]

    # Інформація про замовлення
    order_number = models.CharField('Номер замовлення', max_length=20, unique=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Інформація про клієнта
    first_name = models.CharField('Ім’я', max_length=100)
    last_name = models.CharField('Прізвище', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email', blank=True, null=True)
    
    # Інформація про доставку
    delivery_method = models.CharField('Спосіб доставки', max_length=20, choices=DELIVERY_CHOICES, default='nova_poshta')
    city = models.CharField('Місто', max_length=100)
    office = models.CharField('№ відділення Нової Пошти', max_length=100)
    messengers = models.CharField('Месенджери для зв’язку', max_length=20, choices=MESSENGERS_CHOICES, default='empty')
    
    # Інформація про оплату
    payment_method = models.CharField('Спосіб оплати', max_length=20, choices=PAYMENT_CHOICES)
    is_paid = models.BooleanField('Оплачено', default=False)
    
    # Підсумки замовлення
    subtotal = models.DecimalField('Сума товарів', max_digits=10, decimal_places=2)
    delivery_cost = models.DecimalField('Вартість доставки', max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField('Знижка', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('Разом', max_digits=10, decimal_places=2)
    
    # Додаткова інформація
    notes = models.TextField('Коментар до замовлення', blank=True)
    
    # Дата і час
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created_at']

    def __str__(self):
        return f'Замовлення #{self.order_number}'

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
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Замовлення')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    product_name = models.CharField('Назва товару', max_length=200)
    product_price = models.DecimalField('Ціна товару', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Кількість')
    selected_options = models.JSONField('Обрані опції', default=dict, blank=True)
    total_price = models.DecimalField('Загальна вартість', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Позиція замовлення'
        verbose_name_plural = 'Позиції замовлення'

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'
