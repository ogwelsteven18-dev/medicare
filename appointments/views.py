from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Appointment, Consultation
from .forms import AppointmentForm, ConsultationForm
from patients.models import Patient
from billing.models import Bill, BillItem
from notifications.models import send_notification
import datetime

@login_required
def appointment_list(request):
    user = request.user
    appts = Appointment.objects.select_related('patient','doctor').all()
    if user.role == 'doctor':
        appts = appts.filter(doctor=user)
    elif user.role == 'patient':
        try: appts = appts.filter(patient=user.patient_profile)
        except: appts = appts.none()
    elif user.role == 'nurse':
        appts = appts.all()
    status = request.GET.get('status','')
    if status: appts = appts.filter(status=status)
    return render(request, 'appointments/appointment_list.html', {'appointments': appts, 'status_filter': status})

@login_required
def appointment_create(request):
    user = request.user
    form = AppointmentForm(request.POST or None, user=user)
    if request.method == 'POST' and form.is_valid():
        appt = form.save(commit=False)
        appt.created_by = user
        if user.role == 'patient':
            try: appt.patient = user.patient_profile
            except: messages.error(request, 'Patient profile not found.'); return redirect('users:dashboard')
        appt.save()
        # Auto-generate bill
        bill = Bill.objects.create(patient=appt.patient, created_by=user)
        BillItem.objects.create(bill=bill, item_type='Appointment', description=f'Appointment - {appt.get_appointment_type_display()}', quantity=1, unit_price=appt.fee or 0, amount=appt.fee or 0)
        if appt.doctor and appt.doctor.id:
            send_notification(appt.doctor, 'New Appointment', f'New appointment from {appt.patient.name} on {appt.date}', 'appointment', '/appointments/')
        if appt.patient.user:
            send_notification(appt.patient.user, 'Appointment Booked', f'Your appointment on {appt.date} at {appt.time} has been booked.', 'appointment', '/appointments/')
        messages.success(request, 'Appointment booked successfully.')
        return redirect('appointments:appointment_list')
    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Book Appointment'})

@login_required
def appointment_detail(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointments/appointment_detail.html', {'appointment': appt})

@login_required
def appointment_update_status(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if request.user.role not in ['admin','doctor','nurse']:
        messages.error(request, 'Access denied.')
        return redirect('appointments:appointment_list')
    status = request.POST.get('status')
    if status in ['Scheduled','Confirmed','Completed','Cancelled','Rescheduled']:
        appt.status = status
        appt.save()
        if appt.patient.user:
            send_notification(appt.patient.user, 'Appointment Updated', f'Your appointment on {appt.date} is now {status}.', 'appointment', '/appointments/')
        messages.success(request, f'Appointment marked as {status}.')
    return redirect('appointments:appointment_list')

@login_required
def consultation_list(request):
    user = request.user
    consults = Consultation.objects.select_related('patient','doctor').all()
    if user.role == 'doctor': consults = consults.filter(doctor=user)
    elif user.role == 'patient':
        try: consults = consults.filter(patient=user.patient_profile)
        except: consults = consults.none()
    return render(request, 'appointments/consultation_list.html', {'consultations': consults})

@login_required
def consultation_create(request):
    user = request.user
    form = ConsultationForm(request.POST or None, user=user)
    if request.method == 'POST' and form.is_valid():
        consult = form.save(commit=False)
        if user.role == 'patient':
            try: consult.patient = user.patient_profile
            except: messages.error(request, 'Patient profile not found.'); return redirect('users:dashboard')
        consult.save()
        bill = Bill.objects.create(patient=consult.patient, created_by=user)
        BillItem.objects.create(bill=bill, item_type='Consultation', description='Doctor Consultation', quantity=1, unit_price=consult.fee, amount=consult.fee)
        if consult.doctor:
            send_notification(consult.doctor, 'New Consultation Request', f'{consult.patient.name} requests a consultation.', 'appointment')
        messages.success(request, 'Consultation request submitted.')
        return redirect('appointments:consultation_list')
    return render(request, 'appointments/consultation_form.html', {'form': form, 'title': 'Request Consultation'})

@login_required
def consultation_detail(request, pk):
    consult = get_object_or_404(Consultation, pk=pk)
    form = ConsultationForm(request.POST or None, instance=consult, user=request.user)
    if request.method == 'POST' and request.user.role in ['admin','doctor']:
        if form.is_valid():
            form.save()
            messages.success(request, 'Consultation updated.')
            return redirect('appointments:consultation_list')
    return render(request, 'appointments/consultation_detail.html', {'consultation': consult, 'form': form})
