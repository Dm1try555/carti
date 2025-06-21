from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from cart.utils import get_or_create_cart
from .models import Order, OrderItem
from django.conf import settings

import asyncio
from aiogram import Bot

# Ініціалізація Telegram бота
bot = Bot(token=settings.TELEGRAM_TOKEN)

def send_telegram_message_sync(text):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        asyncio.create_task(bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=text,
            parse_mode="Markdown"
        ))
    else:
        loop.run_until_complete(bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=text,
            parse_mode="Markdown"
        ))



def checkout(request):
    """Страница оформления заказа"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').prefetch_related('product__images')
    
    if not cart_items:
        messages.error(request, 'Ваша корзина пуста')
        return redirect('cart:cart')
    
    subtotal = cart.total_price
    delivery_cost = 300 if subtotal < 10000 else 0
    
    discount = 0
    
    total = subtotal + delivery_cost - discount
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_cost': delivery_cost,
        'discount': discount,
        'total': total,
    }
    return render(request, 'checkout/checkout.html', context)


@require_POST
def process_order(request):
    """Обработка заказа"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product')
    
    if not cart_items:
        messages.error(request, 'Ваша корзина пуста')
        return redirect('cart:cart')
    
    # Создание заказа
    subtotal = cart.total_price
    delivery_cost = 300 if request.POST.get('delivery_method') == 'nova_poshta' else 0
    if subtotal >= 10000:
        delivery_cost = 0
    
    # Применение промокода
    discount = 0
    
    total = subtotal + delivery_cost - discount
    
    order = Order.objects.create(
        first_name=request.POST.get('first_name'),
        last_name=request.POST.get('last_name'),
        phone=request.POST.get('phone'),
        email=request.POST.get('email', ''),
        delivery_method=request.POST.get('delivery_method'),
        city=request.POST.get('city', ''),
        office=request.POST.get('office', ''),
        messengers=request.POST.get('messengers', ''),
        payment_method=request.POST.get('payment_method'),
        subtotal=subtotal,
        delivery_cost=delivery_cost,
        discount=discount,
        total=total,
        notes=request.POST.get('notes', ''),
    )

    # # Створення елементів замовлення і оновлення складу
    # for cart_item in cart_items:
    #     OrderItem.objects.create(
    #         order=order,
    #         product=cart_item.product,
    #         product_name=cart_item.product.name,
    #         product_price=cart_item.product.final_price,
    #         quantity=cart_item.quantity,
    #         selected_options=cart_item.selected_options,
    #         total_price=cart_item.total_price,
    #     )
    #     cart_item.product.stock -= cart_item.quantity
    #     cart_item.product.save()
    


    # Формуємо повідомлення для Telegram
    text = (
        f"*Нове замовлення* #{order.order_number}\n\n"
        f"*👤 Ім'я:* {order.first_name} {order.last_name}\n"
        f"*📞 Телефон:* {order.phone}\n"
        f"*📧 Email:* {order.email}\n"
        f"*🏙 Місто:* {order.city}\n"
        f"*🏤 Відділення:* {order.office}\n"
        f"*🚚 Доставка:* {order.get_delivery_method_display()}\n"
        f"*💰 Оплата:* {order.get_payment_method_display()}\n"
        f"*💵 Сума:* {order.total} грн\n"
        f"*📝 Примітки:* {order.notes or '—'}"
    )


    # Відправляємо повідомлення асинхронно
    send_telegram_message_sync(text)

    # Очищення кошика
    cart.items.all().delete()

    messages.success(request, f'Замовлення #{order.order_number} успішно оформлено! Ми зв\'яжемося з вами найближчим часом.')
    return redirect('store:index')

