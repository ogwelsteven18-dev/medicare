from django.db import models
from users.models import User

class Patient(models.Model):
    BLOOD_TYPES = [('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-')]
    STATUS_CHOICES = [('Active','Active'),('Discharged','Discharged'),('Transferred','Transferred'),('Deceased','Deceased')]
    GENDER_CHOICES = [('Male','Male'),('Female','Female'),('Other','Other')]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='patient_profile')
    name = models.CharField(max_length=200)
    age = models.IntegerField(default=0)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    blood_type = models.CharField(max_length=5, choices=BLOOD_TYPES, blank=True)
    admission_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    emergency_contact = models.CharField(max_length=200, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    allergies = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    assigned_doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctor_patients', limit_choices_to={'role': 'doctor'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return self.name

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='medical_records')
    date = models.DateTimeField(auto_now_add=True)
    diagnosis = models.TextField()
    symptoms = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta: ordering = ['-date']
    def __str__(self): return f"Record for {self.patient.name} - {self.date.date()}"

class Vitals(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vitals')
    nurse = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'nurse'})
    date = models.DateTimeField(auto_now_add=True)
    temperature = models.CharField(max_length=10, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True)
    pulse = models.CharField(max_length=10, blank=True)
    weight = models.CharField(max_length=10, blank=True)
    height = models.CharField(max_length=10, blank=True)
    oxygen_saturation = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)

    class Meta: ordering = ['-date']

class LabResult(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_results')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lab_results')
    test_name = models.CharField(max_length=200)
    result = models.TextField()
    reference_range = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=[('Normal','Normal'),('Abnormal','Abnormal'),('Critical','Critical')], default='Normal')
    file = models.FileField(upload_to='lab_results/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta: ordering = ['-date']
    def __str__(self): return f"{self.test_name} - {self.patient.name}"
