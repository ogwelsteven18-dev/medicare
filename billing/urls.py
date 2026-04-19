from django.urls import path
from . import views

app_name = 'billing'
urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('create/', views.bill_create, name='bill_create'),
    path('<int:pk>/', views.bill_detail, name='bill_detail'),
    path('<int:pk>/add-item/', views.bill_add_item, name='bill_add_item'),
    path('<int:pk>/status/', views.bill_update_status, name='bill_update_status'),
    path('<int:pk>/invoice/', views.invoice_pdf, name='invoice_pdf'),
]
