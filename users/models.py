from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('patient', 'Patient'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=20, blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_admin(self): return self.role == 'admin'
    def is_doctor(self): return self.role == 'doctor'
    def is_nurse(self): return self.role == 'nurse'
    def is_patient_role(self): return self.role == 'patient'

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
