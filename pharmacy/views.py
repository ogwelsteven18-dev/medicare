from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Medicine, Prescription, PrescriptionItem, MedicineOrder, MedicineOrderItem
from .forms import MedicineForm, PrescriptionForm, MedicineOrderForm
from patients.models import Patient
from billing.models import Bill, BillItem
from notifications.models import send_notification

@login_required
def medicine_list(request):
    q = request.GET.get('q','')
    meds = Medicine.objects.filter(is_active=True)
    if q: meds = meds.filter(Q(name__icontains=q)|Q(generic_name__icontains=q))
    return render(request, 'pharmacy/medicine_list.html', {'medicines': meds, 'q': q})

@login_required
def medicine_create(request):
    if request.user.role not in ['admin']:
        messages.error(request, 'Access denied.')
        return redirect('pharmacy:medicine_list')
    form = MedicineForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Medicine added.')
        return redirect('pharmacy:medicine_list')
    return render(request, 'pharmacy/medicine_form.html', {'form': form, 'title': 'Add Medicine'})

@login_required
def medicine_edit(request, pk):
    if request.user.role not in ['admin']:
        messages.error(request, 'Access denied.')
        return redirect('pharmacy:medicine_list')
    med = get_object_or_404(Medicine, pk=pk)
    form = MedicineForm(request.POST or None, instance=med)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Medicine updated.')
        return redirect('pharmacy:medicine_list')
    return render(request, 'pharmacy/medicine_form.html', {'form': form, 'title': 'Edit Medicine', 'medicine': med})

@login_required
def prescription_list(request):
    user = request.user
    prescriptions = Prescription.objects.select_related('patient','doctor').all()
    if user.role == 'doctor': prescriptions = prescriptions.filter(doctor=user)
    elif user.role == 'patient':
        try: prescriptions = prescriptions.filter(patient=user.patient_profile)
        except: prescriptions = prescriptions.none()
    return render(request, 'pharmacy/prescription_list.html', {'prescriptions': prescriptions})

@login_required
def prescription_create(request, patient_id=None):
    if request.user.role not in ['admin','doctor']:
        messages.error(request, 'Access denied.')
        return redirect('pharmacy:prescription_list')
    patient = get_object_or_404(Patient, pk=patient_id) if patient_id else None
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            rx = form.save(commit=False)
            rx.doctor = request.user
            rx.save()
            # Save items
            items_data = []
            for i in range(20):
                med_id = request.POST.get(f'item_medicine_{i}')
                if not med_id: break
                dosage = request.POST.get(f'item_dosage_{i}','')
                frequency = request.POST.get(f'item_frequency_{i}','')
                duration = request.POST.get(f'item_duration_{i}','')
                qty = int(request.POST.get(f'item_quantity_{i}', 1) or 1)
                instr = request.POST.get(f'item_instructions_{i}','')
                try:
                    med = Medicine.objects.get(pk=med_id)
                    PrescriptionItem.objects.create(prescription=rx, medicine=med, dosage=dosage, frequency=frequency, duration=duration, quantity=qty, instructions=instr)
                    items_data.append((med, qty))
                except Medicine.DoesNotExist:
                    pass
            # Generate bill for medicines
            if items_data:
                bill = Bill.objects.create(patient=rx.patient, created_by=request.user)
                for med, qty in items_data:
                    BillItem.objects.create(bill=bill, item_type='Medicine', description=med.name, quantity=qty, unit_price=med.unit_price, amount=med.unit_price * qty)
            if rx.patient.user:
                send_notification(rx.patient.user, 'New Prescription', f'Dr. {request.user.get_full_name()} has issued a prescription for you.', 'prescription', '/pharmacy/prescriptions/')
            messages.success(request, 'Prescription created.')
            return redirect('pharmacy:prescription_list')
    else:
        form = PrescriptionForm(initial={'patient': patient, 'doctor': request.user})
    medicines = Medicine.objects.filter(is_active=True)
    return render(request, 'pharmacy/prescription_form.html', {'form': form, 'patient': patient, 'medicines': medicines})

@login_required
def prescription_detail(request, pk):
    rx = get_object_or_404(Prescription, pk=pk)
    return render(request, 'pharmacy/prescription_detail.html', {'prescription': rx})

@login_required
def order_list(request):
    user = request.user
    orders = MedicineOrder.objects.select_related('patient').all()
    if user.role == 'patient':
        try: orders = orders.filter(patient=user.patient_profile)
        except: orders = orders.none()
    return render(request, 'pharmacy/order_list.html', {'orders': orders})

@login_required
def order_create(request):
    user = request.user
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        if user.role == 'patient':
            try: patient = user.patient_profile
            except: messages.error(request, 'Patient profile not found.'); return redirect('users:dashboard')
        else:
            patient = get_object_or_404(Patient, pk=patient_id)
        order = MedicineOrder.objects.create(patient=patient)
        total = 0
        for i in range(50):
            med_id = request.POST.get(f'med_{i}')
            qty = request.POST.get(f'qty_{i}')
            if not med_id or not qty: break
            try:
                med = Medicine.objects.get(pk=med_id)
                qty = int(qty)
                subtotal = med.unit_price * qty
                MedicineOrderItem.objects.create(order=order, medicine=med, quantity=qty, unit_price=med.unit_price)
                total += subtotal
            except: pass
        order.total_amount = total
        order.save()
        bill = Bill.objects.create(patient=patient, created_by=user)
        for item in order.items.all():
            BillItem.objects.create(bill=bill, item_type='Medicine', description=item.medicine.name, quantity=item.quantity, unit_price=item.unit_price, amount=item.subtotal)
        messages.success(request, 'Medicine order placed.')
        return redirect('pharmacy:order_list')
    medicines = Medicine.objects.filter(is_active=True, stock_quantity__gt=0)
    patients = Patient.objects.filter(status='Active') if user.role != 'patient' else None
    return render(request, 'pharmacy/order_form.html', {'medicines': medicines, 'patients': patients})

@login_required
def order_update_status(request, pk):
    order = get_object_or_404(MedicineOrder, pk=pk)
    if request.user.role not in ['admin']:
        messages.error(request, 'Access denied.')
        return redirect('pharmacy:order_list')
    status = request.POST.get('status')
    if status:
        order.status = status
        order.save()
        messages.success(request, f'Order status updated to {status}.')
    return redirect('pharmacy:order_list')
