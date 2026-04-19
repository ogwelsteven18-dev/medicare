from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Bill, BillItem
from .forms import BillForm, BillItemForm
from patients.models import Patient
import datetime

@login_required
def bill_list(request):
    user = request.user
    bills = Bill.objects.select_related('patient').all()
    if user.role == 'patient':
        try: bills = bills.filter(patient=user.patient_profile)
        except: bills = bills.none()
    status = request.GET.get('status','')
    if status: bills = bills.filter(status=status)
    return render(request, 'billing/bill_list.html', {'bills': bills, 'status_filter': status})

@login_required
def bill_detail(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.user.role == 'patient':
        try:
            if bill.patient != request.user.patient_profile:
                messages.error(request, 'Access denied.'); return redirect('billing:bill_list')
        except: messages.error(request, 'Access denied.'); return redirect('billing:bill_list')
    return render(request, 'billing/bill_detail.html', {'bill': bill})

@login_required
def bill_create(request):
    if request.user.role not in ['admin']:
        messages.error(request, 'Access denied.'); return redirect('billing:bill_list')
    form = BillForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        bill = form.save(commit=False)
        bill.created_by = request.user
        bill.save()
        messages.success(request, 'Bill created.')
        return redirect('billing:bill_detail', pk=bill.pk)
    return render(request, 'billing/bill_form.html', {'form': form, 'title': 'Create Bill'})

@login_required
def bill_add_item(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    form = BillItemForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.bill = bill
        item.save()
        messages.success(request, 'Item added.')
        return redirect('billing:bill_detail', pk=pk)
    return render(request, 'billing/bill_item_form.html', {'form': form, 'bill': bill})

@login_required
def bill_update_status(request, pk):
    if request.user.role not in ['admin']:
        messages.error(request, 'Access denied.'); return redirect('billing:bill_list')
    bill = get_object_or_404(Bill, pk=pk)
    status = request.POST.get('status')
    if status: bill.status = status; bill.save()
    messages.success(request, 'Bill status updated.')
    return redirect('billing:bill_detail', pk=pk)

@login_required
def invoice_pdf(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    return render(request, 'billing/invoice.html', {'bill': bill, 'today': datetime.date.today()})
