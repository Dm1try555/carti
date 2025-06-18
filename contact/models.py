from django.db import models


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('order', 'Питання по замовленню'),
        ('product', 'Питання по товару'),
        ('custom', 'Індивідуальне замовлення'),
        ('complaint', 'Скарги'),
        ('other', 'Інше'),
    ]

    MESSENGER_CHOICES = [
        ('empty', '---'),
        ('telegram', 'Telegram'),
        ('viber', 'Viber'),
        ('whatsapp', 'WhatsApp'),
    ]

    name = models.CharField('Ім’я', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20)
    subject = models.CharField('Тема', max_length=20, choices=SUBJECT_CHOICES)
    messenger = models.CharField('Месенджер', max_length=20, choices=MESSENGER_CHOICES, default='empty')
    message = models.TextField('Повідомлення')
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Створено', auto_now_add=True)

    class Meta:
        verbose_name = 'Повідомлення'
        verbose_name_plural = 'Повідомлення'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.get_subject_display()}'
