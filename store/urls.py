from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Основные страницы
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    
    # Корзина
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('apply-promo/', views.apply_promo, name='apply_promo'),
    
    # Заказы
    path('checkout/', views.checkout, name='checkout'),
    path('process-order/', views.process_order, name='process_order'),
    
    # Информационные страницы
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('send-message/', views.send_message, name='send_message'),
    path('delivery/', views.delivery, name='delivery'),
    path('returns/', views.returns, name='returns'),
    path('care/', views.care, name='care'),
    path('privacy/', views.privacy, name='privacy'),
]
