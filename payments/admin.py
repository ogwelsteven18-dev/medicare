from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'patient', 'payment_method', 'amount', 'status', 'transaction_id', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['patient__name', 'transaction_id']
    readonly_fields = ['external_ref', 'webhook_data']
