from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import ContactMessage


def contact(request):
    """Страница контактов"""
    return render(request, 'contact/contact.html')


@require_POST
def send_message(request):
    """Отправка сообщения"""
    try:
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        )
        messages.success(request, 'Ваше сообщение отправлено! Мы ответим в ближайшее время.')
    except Exception as e:
        messages.error(request, 'Произошла ошибка при отправке сообщения.')
    
    return redirect('contact:contact')
