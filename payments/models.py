from django.db import models
from users.models import User
from patients.models import Patient
from billing.models import Bill

class Payment(models.Model):
    METHOD_CHOICES = [('MTN_MOMO','MTN Mobile Money'),('AIRTEL','Airtel Money'),('CASH','Cash'),('CARD','Card')]
    STATUS_CHOICES = [('Pending','Pending'),('Processing','Processing'),('Success','Success'),('Failed','Failed'),('Cancelled','Cancelled')]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    bill = models.ForeignKey(Bill, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=20, blank=True)
    transaction_id = models.CharField(max_length=200, blank=True)
    external_ref = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    status_reason = models.TextField(blank=True)
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    webhook_data = models.JSONField(null=True, blank=True)

    class Meta: ordering = ['-created_at']
    def __str__(self): return f"Payment {self.transaction_id or self.pk} - {self.patient.name} ({self.status})"
