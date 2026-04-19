from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from patients.models import Patient
from appointments.models import Appointment, Consultation
from billing.models import Bill
from payments.models import Payment
from users.models import User
import datetime, json

@login_required
def reports_dashboard(request):
    if request.user.role not in ['admin','doctor']:
        messages.error(request, 'Access denied.')
        return redirect('users:dashboard')
    today = datetime.date.today()
    year = today.year
    # Monthly stats
    monthly_patients = []
    monthly_revenue = []
    monthly_appointments = []
    labels = []
    for m in range(1, 13):
        labels.append(datetime.date(year, m, 1).strftime('%b'))
        monthly_patients.append(Patient.objects.filter(admission_date__year=year, admission_date__month=m).count())
        monthly_revenue.append(float(Payment.objects.filter(status='Success', created_at__year=year, created_at__month=m).aggregate(t=Sum('amount'))['t'] or 0))
        monthly_appointments.append(Appointment.objects.filter(date__year=year, date__month=m).count())

    ctx = {
        'total_patients': Patient.objects.count(),
        'active_patients': Patient.objects.filter(status='Active').count(),
        'total_revenue': Payment.objects.filter(status='Success').aggregate(t=Sum('amount'))['t'] or 0,
        'total_appointments': Appointment.objects.count(),
        'completed_appointments': Appointment.objects.filter(status='Completed').count(),
        'pending_bills': Bill.objects.filter(status='Pending').count(),
        'total_doctors': User.objects.filter(role='doctor').count(),
        'total_nurses': User.objects.filter(role='nurse').count(),
        'monthly_patients_json': json.dumps(monthly_patients),
        'monthly_revenue_json': json.dumps(monthly_revenue),
        'monthly_appointments_json': json.dumps(monthly_appointments),
        'labels_json': json.dumps(labels),
        'status_counts': list(Appointment.objects.values('status').annotate(c=Count('id'))),
        'payment_methods': list(Payment.objects.filter(status='Success').values('payment_method').annotate(c=Count('id'), total=Sum('amount'))),
        'year': year,
    }
    return render(request, 'reports/dashboard.html', ctx)

from django.shortcuts import redirect
