from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from .models import User
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm
from patients.models import Patient, Vitals
from appointments.models import Appointment, Consultation
from pharmacy.models import Prescription
from billing.models import Bill
from notifications.models import Notification
import datetime


def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # Auto-create patient profile for patient-role users
                if user.role == 'patient' and not hasattr(user, 'patient_profile'):
                    Patient.objects.create(
                        user=user,
                        name=user.get_full_name() or user.username,
                        phone=user.phone or ''
                    )
                return redirect('users:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html', {})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        if user.role == 'patient':
            Patient.objects.create(
                user=user,
                name=user.get_full_name() or user.username,
                phone=user.phone or ''
            )
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('users:login')
    return render(request, 'users/register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login')


@login_required
def dashboard(request):
    user = request.user
    today = datetime.date.today()

    if user.role == 'admin':
        ctx = {
            'today': today,
            'total_patients': Patient.objects.count(),
            'total_doctors': User.objects.filter(role='doctor').count(),
            'total_nurses': User.objects.filter(role='nurse').count(),
            'total_appointments': Appointment.objects.count(),
            'pending_appointments': Appointment.objects.filter(status='Scheduled').count(),
            'pending_bills': Bill.objects.filter(status='Pending').count(),
            'total_revenue': Bill.objects.filter(status='Paid').aggregate(
                t=Sum('items__amount'))['t'] or 0,
            'recent_appointments': Appointment.objects.select_related('patient', 'doctor').order_by('-created_at')[:8],
            'recent_patients': Patient.objects.order_by('-created_at')[:8],
        }
        return render(request, 'users/dashboard_admin.html', ctx)

    elif user.role == 'doctor':
        my_patients = Patient.objects.filter(assigned_doctor=user)
        ctx = {
            'today': today,
            'my_patients': my_patients.count(),
            'todays_appointments': Appointment.objects.filter(doctor=user, date=today).count(),
            'pending_consultations': Consultation.objects.filter(doctor=user, status='Pending').count(),
            'prescriptions_issued': Prescription.objects.filter(doctor=user).count(),
            'todays_appointment_list': Appointment.objects.filter(doctor=user, date=today).select_related('patient').order_by('time'),
            'recent_patients': my_patients.order_by('-created_at')[:8],
            'recent_consultations': Consultation.objects.filter(doctor=user).select_related('patient').order_by('-date')[:6],
        }
        return render(request, 'users/dashboard_doctor.html', ctx)

    elif user.role == 'nurse':
        from patients.models import Vitals
        ctx = {
            'today': today,
            'total_patients': Patient.objects.filter(status='Active').count(),
            'todays_appointments': Appointment.objects.filter(date=today).count(),
            'vitals_today': Vitals.objects.filter(date__date=today, nurse=user).count(),
            'new_today': Patient.objects.filter(admission_date=today).count(),
            'todays_appointment_list': Appointment.objects.filter(date=today).select_related('patient', 'doctor').order_by('time')[:10],
            'recent_patients': Patient.objects.filter(status='Active').select_related('assigned_doctor').order_by('-created_at')[:8],
        }
        return render(request, 'users/dashboard_nurse.html', ctx)

    elif user.role == 'patient':
        try:
            patient = user.patient_profile
        except Exception:
            patient = None

        ctx = {'today': today, 'patient': patient}
        if patient:
            ctx.update({
                'my_appointments': Appointment.objects.filter(patient=patient).count(),
                'my_prescriptions': Prescription.objects.filter(patient=patient).count(),
                'my_pending_bills': Bill.objects.filter(patient=patient, status='Pending').count(),
                'recent_appointments': Appointment.objects.filter(patient=patient).select_related('doctor').order_by('-date')[:5],
                'recent_bills': Bill.objects.filter(patient=patient).order_by('-date')[:4],
                'recent_lab_results': patient.lab_results.order_by('-date')[:4],
            })
        return render(request, 'users/dashboard_patient.html', ctx)

    # Fallback
    return render(request, 'users/dashboard_admin.html', {'today': today})


@login_required
def profile(request):
    user = request.user
    form = UserUpdateForm(request.POST or None, request.FILES or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('users:profile')
    return render(request, 'users/profile.html', {'form': form})


@login_required
def user_list(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('users:dashboard')
    role = request.GET.get('role', '')
    users = User.objects.all().order_by('-date_joined')
    if role:
        users = users.filter(role=role)
    return render(request, 'users/user_list.html', {'users': users, 'selected_role': role})


@login_required
def user_create(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('users:dashboard')
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        if user.role == 'patient':
            Patient.objects.create(
                user=user,
                name=user.get_full_name() or user.username,
                phone=user.phone or ''
            )
        messages.success(request, f'User {user.username} created successfully.')
        return redirect('users:user_list')
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Create User'})


@login_required
def user_delete(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('users:dashboard')
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
    else:
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully.')
    return redirect('users:user_list')
