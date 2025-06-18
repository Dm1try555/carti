from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class PromoCode(models.Model):
    code = models.CharField('Код', max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField('Відсоток знижки', validators=[MinValueValidator(1), MaxValueValidator(100)])
    min_order_amount = models.DecimalField('Мінімальна сума замовлення', max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField('Максимальна кількість використань', blank=True, null=True)
    used_count = models.PositiveIntegerField('Кількість використань', default=0)
    is_active = models.BooleanField('Активний', default=True)
    valid_from = models.DateTimeField('Діє з')
    valid_until = models.DateTimeField('Діє до')
    created_at = models.DateTimeField('Створено', auto_now_add=True)

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоди'

    def __str__(self):
        return self.code

    def is_valid(self, order_amount=0):
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False, 'Промокод неактивний'
        
        if now < self.valid_from or now > self.valid_until:
            return False, 'Термін дії промокоду минув'
        
        if self.max_uses and self.used_count >= self.max_uses:
            return False, 'Промокод вичерпано'
        
        if order_amount < self.min_order_amount:
            return False, f'Мінімальна сума замовлення {self.min_order_amount} ₴'
        
        return True, 'Промокод дійсний'
