from django.shortcuts import render


def delivery(request):
    """Страница доставки и оплаты"""
    return render(request, 'info/delivery.html')


def returns(request):
    """Страница возврата и обмена"""
    return render(request, 'info/returns.html')


def care(request):
    """Страница ухода за изделиями"""
    return render(request, 'info/care.html')


def privacy(request):
    """Страница политики конфиденциальности"""
    return render(request, 'info/privacy.html')
