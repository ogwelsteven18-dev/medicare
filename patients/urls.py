from django.urls import path
from . import views

app_name = 'patients'
urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('<int:pk>/', views.patient_detail, name='patient_detail'),
    path('add/', views.patient_create, name='patient_create'),
    path('<int:pk>/edit/', views.patient_edit, name='patient_edit'),
    path('<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    path('<int:patient_id>/vitals/', views.add_vitals, name='add_vitals'),
    path('<int:patient_id>/medical-record/', views.add_medical_record, name='add_medical_record'),
    path('<int:patient_id>/lab-result/', views.add_lab_result, name='add_lab_result'),
]
