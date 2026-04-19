from django.contrib import admin
from .models import Appointment, Consultation

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date', 'time', 'appointment_type', 'status', 'fee']
    list_filter = ['status', 'appointment_type', 'date']
    search_fields = ['patient__name', 'doctor__first_name']
    ordering = ['-date', '-time']

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date', 'status', 'fee']
    list_filter = ['status']
    search_fields = ['patient__name']
