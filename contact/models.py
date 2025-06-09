from django.db import models


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
