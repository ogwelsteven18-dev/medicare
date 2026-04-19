from django.db import models
from users.models import User
from patients.models import Patient
from django.conf import settings

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled','Scheduled'),('Confirmed','Confirmed'),
        ('Completed','Completed'),('Cancelled','Cancelled'),('Rescheduled','Rescheduled'),
    ]
    TYPE_CHOICES = [('General','General Checkup'),('Consultation','Consultation'),('Follow-up','Follow-up'),('Emergency','Emergency')]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='appointments', limit_choices_to={'role': 'doctor'})
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='General')
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    notes = models.TextField(blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: ordering = ['-date', '-time']
    def __str__(self): return f"Appointment: {self.patient.name} with Dr.{self.doctor} on {self.date}"

class Consultation(models.Model):
    STATUS_CHOICES = [('Pending','Pending'),('In Progress','In Progress'),('Completed','Completed'),('Cancelled','Cancelled')]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='consultations', limit_choices_to={'role':'doctor'})
    date = models.DateTimeField(auto_now_add=True)
    chief_complaint = models.TextField()
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=settings.CONSULTATION_FEE)
    notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)

    class Meta: ordering = ['-date']
    def __str__(self): return f"Consultation: {self.patient.name} - {self.date.date()}"
