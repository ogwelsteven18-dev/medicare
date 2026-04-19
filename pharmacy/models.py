from django.db import models
from users.models import User
from patients.models import Patient

class Medicine(models.Model):
    CATEGORY_CHOICES = [
        ('Tablet','Tablet'),('Capsule','Capsule'),('Syrup','Syrup'),
        ('Injection','Injection'),('Cream','Cream'),('Drops','Drops'),('Other','Other'),
    ]
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Tablet')
    manufacturer = models.CharField(max_length=200, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_low_stock(self): return self.stock_quantity <= self.reorder_level
    def __str__(self): return f"{self.name} ({self.category})"

class Prescription(models.Model):
    STATUS_CHOICES = [('Active','Active'),('Dispensed','Dispensed'),('Cancelled','Cancelled')]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prescriptions', limit_choices_to={'role':'doctor'})
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    notes = models.TextField(blank=True)
    dispensed_at = models.DateTimeField(null=True, blank=True)

    class Meta: ordering = ['-date']
    def __str__(self): return f"Prescription #{self.pk} - {self.patient.name}"

class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    instructions = models.TextField(blank=True)

    @property
    def subtotal(self): return self.medicine.unit_price * self.quantity

class MedicineOrder(models.Model):
    STATUS_CHOICES = [('Pending','Pending'),('Processing','Processing'),('Ready','Ready'),('Dispensed','Dispensed'),('Cancelled','Cancelled')]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medicine_orders')
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"Order #{self.pk} - {self.patient.name}"

class MedicineOrderItem(models.Model):
    order = models.ForeignKey(MedicineOrder, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self): return self.unit_price * self.quantity
