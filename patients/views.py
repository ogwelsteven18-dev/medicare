from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Patient, MedicalRecord, Vitals, LabResult
from .forms import PatientForm, VitalsForm, MedicalRecordForm, LabResultForm
from notifications.models import send_notification

def role_required(*roles):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('users:login')
            if request.user.role not in roles:
                messages.error(request, 'Access denied.')
                return redirect('users:dashboard')
            return f(request, *args, **kwargs)
        return wrapper
    return decorator

@login_required
def patient_list(request):
    q = request.GET.get('q','')
    status = request.GET.get('status','')
    patients = Patient.objects.select_related('assigned_doctor').all()
    if request.user.role == 'doctor':
        patients = patients.filter(assigned_doctor=request.user)
    if q:
        patients = patients.filter(Q(name__icontains=q)|Q(phone__icontains=q))
    if status:
        patients = patients.filter(status=status)
    return render(request, 'patients/patient_list.html', {'patients': patients, 'q': q, 'status_filter': status})

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.user.role == 'patient':
        if not hasattr(request.user, 'patient_profile') or request.user.patient_profile != patient:
            messages.error(request, 'Access denied.')
            return redirect('users:dashboard')
    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'vitals': patient.vitals.order_by('-date')[:5],
        'medical_records': patient.medical_records.order_by('-date')[:5],
        'lab_results': patient.lab_results.order_by('-date')[:5],
        'appointments': patient.appointments.order_by('-date')[:5],
        'bills': patient.bills.order_by('-date')[:5],
        'prescriptions': patient.prescriptions.order_by('-date')[:5],
    })

@login_required
@role_required('admin','nurse','doctor')
def patient_create(request):
    form = PatientForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        patient = form.save()
        messages.success(request, f'Patient {patient.name} added successfully.')
        return redirect('patients:patient_detail', pk=patient.pk)
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Add Patient'})

@login_required
@role_required('admin','nurse','doctor')
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Patient updated.')
        return redirect('patients:patient_detail', pk=pk)
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Edit Patient', 'patient': patient})

@login_required
@role_required('admin')
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    patient.delete()
    messages.success(request, 'Patient deleted.')
    return redirect('patients:patient_list')

@login_required
@role_required('admin','nurse')
def add_vitals(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    form = VitalsForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        vitals = form.save(commit=False)
        vitals.patient = patient
        vitals.nurse = request.user
        vitals.save()
        messages.success(request, 'Vitals recorded.')
        return redirect('patients:patient_detail', pk=patient_id)
    return render(request, 'patients/vitals_form.html', {'form': form, 'patient': patient})

@login_required
@role_required('admin','doctor')
def add_medical_record(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    form = MedicalRecordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        record.patient = patient
        record.doctor = request.user
        record.save()
        if patient.user:
            send_notification(patient.user, 'New Medical Record', f'Dr. {request.user.get_full_name()} added a medical record for you.', 'general', f'/patients/{patient.pk}/')
        messages.success(request, 'Medical record added.')
        return redirect('patients:patient_detail', pk=patient_id)
    return render(request, 'patients/medical_record_form.html', {'form': form, 'patient': patient})

@login_required
@role_required('admin','doctor')
def add_lab_result(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    form = LabResultForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        lab = form.save(commit=False)
        lab.patient = patient
        lab.doctor = request.user
        lab.save()
        if patient.user:
            send_notification(patient.user, 'Lab Result Available', f'Your lab result for {lab.test_name} is now available.', 'lab', f'/patients/{patient.pk}/')
        messages.success(request, 'Lab result added.')
        return redirect('patients:patient_detail', pk=patient_id)
    return render(request, 'patients/lab_result_form.html', {'form': form, 'patient': patient})
