from django.urls import path
from . import views

app_name = 'pharmacy'
urlpatterns = [
    path('', views.medicine_list, name='medicine_list'),
    path('medicine/add/', views.medicine_create, name='medicine_create'),
    path('medicine/<int:pk>/edit/', views.medicine_edit, name='medicine_edit'),
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/create/', views.prescription_create, name='prescription_create'),
    path('prescriptions/create/<int:patient_id>/', views.prescription_create, name='prescription_create_for'),
    path('prescriptions/<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/status/', views.order_update_status, name='order_update_status'),
]
