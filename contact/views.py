from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from .models import ContactMessage
import asyncio
from aiogram import Bot

# Ініціалізація Telegram бота
bot = Bot(token=settings.TELEGRAM_TOKEN)

def contact(request):
    return render(request, 'contact/contact.html')

@require_POST
def send_message(request):
    try:
        # Створюємо і зберігаємо повідомлення
        message_instance = ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            subject=request.POST.get('subject'),
            messenger=request.POST.get('messenger'),
            message=request.POST.get('message'),
        )

        # Отримуємо людську назву теми
        subject_display = message_instance.get_subject_display()

        # Формуємо повідомлення для Telegram
        text = (
            f"Нове повідомлення від {message_instance.name}:\n\n"
            f"📧 Email: {message_instance.email}\n"
            f"📞 Телефон: {message_instance.phone}\n"
            f"📌 Тема: {subject_display}\n\n"
            f"👤 Месенджер: {message_instance.messenger}\n\n"
            f"{message_instance.message}"
        )

        # Надсилаємо
        asyncio.run(send_telegram_message(text))

        messages.success(request, 'Ваше повідомлення відправлено! Ми звʼяжемося з вами найближчим часом.')
    except Exception as e:
        print("Помилка:", e)
        messages.error(request, 'Відбулася помилка під час надсилання повідомлення.')

    return redirect('contact:contact')


async def send_telegram_message(text):
    await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=text)
