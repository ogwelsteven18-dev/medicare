from django.contrib import admin
from .models import Bill, BillItem

class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'patient', 'status', 'date', 'due_date']
    list_filter = ['status']
    search_fields = ['invoice_number', 'patient__name']
    inlines = [BillItemInline]
    readonly_fields = ['invoice_number']
