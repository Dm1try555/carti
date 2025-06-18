from django.db import models
from django.contrib.auth.models import User
from store.models import Product


class Cart(models.Model):
    session_key = models.CharField('Ключ сесії', max_length=40)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Користувач', blank=True, null=True)
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)

    class Meta:
        verbose_name = 'Кошик'
        verbose_name_plural = 'Кошики'

    def __str__(self):
        return f'Кошик {self.id}'

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Кошик')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField('Кількість', default=1)
    selected_options = models.JSONField('Вибрані опції', default=dict, blank=True)
    created_at = models.DateTimeField('Створено', auto_now_add=True)

    class Meta:
        verbose_name = 'Елемент кошика'
        verbose_name_plural = 'Елементи кошика'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    @property
    def total_price(self):
        return self.product.final_price * self.quantity
