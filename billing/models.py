from django.db import models
from users.models import User
from patients.models import Patient

class Bill(models.Model):
    STATUS_CHOICES = [('Pending','Pending'),('Partial','Partial'),('Paid','Paid'),('Cancelled','Cancelled'),('Overdue','Overdue')]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            import datetime
            self.invoice_number = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{self.patient_id}"
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return sum(item.amount for item in self.items.all())

    @property
    def total(self):
        return self.subtotal + self.tax - self.discount

    @property
    def amount_paid(self):
        from payments.models import Payment
        paid = Payment.objects.filter(bill=self, status='Success').aggregate(total=models.Sum('amount'))
        return paid['total'] or 0

    @property
    def balance(self):
        return self.total - self.amount_paid

    class Meta: ordering = ['-date']
    def __str__(self): return f"Bill #{self.invoice_number} - {self.patient.name}"

class BillItem(models.Model):
    ITEM_TYPES = [
        ('Consultation','Consultation'),('Appointment','Appointment'),
        ('Medicine','Medicine'),('Lab','Lab Test'),('Other','Other'),
    ]
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default='Other')
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.amount = self.unit_price * self.quantity
        super().save(*args, **kwargs)
