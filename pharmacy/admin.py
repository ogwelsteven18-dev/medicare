from django.contrib import admin
from .models import Medicine, Prescription, PrescriptionItem, MedicineOrder, MedicineOrderItem

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'category', 'unit_price', 'stock_quantity', 'reorder_level', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'generic_name', 'manufacturer']

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'patient', 'doctor', 'date', 'status']
    list_filter = ['status']
    inlines = [PrescriptionItemInline]

class MedicineOrderItemInline(admin.TabularInline):
    model = MedicineOrderItem
    extra = 1

@admin.register(MedicineOrder)
class MedicineOrderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'patient', 'total_amount', 'status', 'created_at']
    list_filter = ['status']
    inlines = [MedicineOrderItemInline]
