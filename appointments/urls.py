from django.urls import path
from . import views

app_name = 'appointments'
urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('create/', views.appointment_create, name='appointment_create'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/status/', views.appointment_update_status, name='appointment_update_status'),
    path('consultations/', views.consultation_list, name='consultation_list'),
    path('consultations/create/', views.consultation_create, name='consultation_create'),
    path('consultations/<int:pk>/', views.consultation_detail, name='consultation_detail'),
]
