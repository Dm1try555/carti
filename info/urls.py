from django.urls import path
from . import views

app_name = 'info'

urlpatterns = [
    path('delivery/', views.delivery, name='delivery'),
    path('returns/', views.returns, name='returns'),
    path('care/', views.care, name='care'),
    path('privacy/', views.privacy, name='privacy'),
]
