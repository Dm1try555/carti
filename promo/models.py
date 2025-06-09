from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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
