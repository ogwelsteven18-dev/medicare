from django.urls import path
from . import views

app_name = 'payments'
urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('pay/<int:bill_id>/', views.initiate_payment, name='initiate_payment'),
    path('status/<int:pk>/', views.payment_status, name='payment_status'),
    path('receipt/<int:pk>/', views.receipt, name='receipt'),
    path('webhook/mtn/', views.mtn_webhook, name='mtn_webhook'),
    path('webhook/airtel/', views.airtel_webhook, name='airtel_webhook'),
]
