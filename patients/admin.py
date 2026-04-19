from django.contrib import admin
from .models import Patient, MedicalRecord, Vitals, LabResult

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'gender', 'blood_type', 'phone', 'assigned_doctor', 'status', 'admission_date']
    list_filter = ['status', 'gender', 'blood_type']
    search_fields = ['name', 'phone', 'address']
    ordering = ['-created_at']

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'diagnosis', 'date']
    list_filter = ['doctor']
    search_fields = ['patient__name', 'diagnosis']

@admin.register(Vitals)
class VitalsAdmin(admin.ModelAdmin):
    list_display = ['patient', 'nurse', 'temperature', 'blood_pressure', 'pulse', 'date']

@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ['patient', 'test_name', 'status', 'doctor', 'date']
    list_filter = ['status']
