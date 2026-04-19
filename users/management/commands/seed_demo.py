"""
Management command to seed demo data.
Usage: python manage.py seed_demo
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from patients.models import Patient, MedicalRecord, Vitals, LabResult
from appointments.models import Appointment, Consultation
from pharmacy.models import Medicine, Prescription, PrescriptionItem
from billing.models import Bill, BillItem
from payments.models import Payment
from notifications.models import Notification
import datetime


class Command(BaseCommand):
    help = 'Seed the database with demo data for all roles'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding MediCare HMS demo data...'))

        # Admin
        admin, _ = User.objects.get_or_create(username='admin', defaults=dict(
            first_name='System', last_name='Administrator', role='admin',
            email='admin@medicare.ug', phone='+256700000000', is_superuser=True, is_staff=True))
        if _:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'  ✓ Admin: admin / admin123')

        # Doctors
        doctors = []
        for uname, fn, ln, email in [
            ('dr.sarah', 'Dr. Sarah', 'Kamau', 'sarah@medicare.ug'),
            ('dr.james', 'Dr. James', 'Ochieng', 'james@medicare.ug'),
        ]:
            u, created = User.objects.get_or_create(username=uname, defaults=dict(
                first_name=fn, last_name=ln, role='doctor', email=email))
            if created:
                u.set_password('pass@123')
                u.save()
                self.stdout.write(f'  ✓ Doctor: {uname} / pass@123')
            doctors.append(u)

        # Nurses
        nurses = []
        for uname, fn, ln in [('nurse.alice', 'Alice', 'Nakato'), ('nurse.bob', 'Bob', 'Ssali')]:
            u, created = User.objects.get_or_create(username=uname, defaults=dict(
                first_name=fn, last_name=ln, role='nurse'))
            if created:
                u.set_password('pass@123')
                u.save()
                self.stdout.write(f'  ✓ Nurse: {uname} / pass@123')
            nurses.append(u)

        # Patient users
        patient_users = []
        for uname, fn, ln, email, phone in [
            ('john.patient', 'John', 'Mutua', 'john@email.com', '+256703333333'),
            ('mary.patient', 'Mary', 'Achieng', 'mary@email.com', '+256704444444'),
        ]:
            u, created = User.objects.get_or_create(username=uname, defaults=dict(
                first_name=fn, last_name=ln, role='patient', email=email, phone=phone))
            if created:
                u.set_password('pass@123')
                u.save()
                self.stdout.write(f'  ✓ Patient user: {uname} / pass@123')
            patient_users.append(u)

        # Patients
        today = datetime.date.today()
        patients_raw = [
            ('John Mutua', 32, 'Male', '+256703333333', 'Kampala', 'A+', 'Active', doctors[0], patient_users[0], 'Penicillin'),
            ('Mary Achieng', 28, 'Female', '+256704444444', 'Entebbe', 'O+', 'Active', doctors[0], patient_users[1], ''),
            ('Peter Okello', 45, 'Male', '+256705555555', 'Jinja', 'B+', 'Active', doctors[1], None, 'Sulfa drugs'),
            ('Grace Nambi', 22, 'Female', '+256706666666', 'Masaka', 'AB+', 'Active', doctors[1], None, ''),
            ('David Ssekandi', 55, 'Male', '+256707777777', 'Gulu', 'O-', 'Discharged', doctors[0], None, 'Aspirin'),
        ]
        patients = []
        for name, age, gender, phone, addr, blood, status, doc, user, allergies in patients_raw:
            p, created = Patient.objects.get_or_create(name=name, defaults=dict(
                age=age, gender=gender, phone=phone, address=addr, blood_type=blood,
                status=status, assigned_doctor=doc, user=user, allergies=allergies,
                emergency_contact='Next of Kin', emergency_phone='+256709999999'))
            patients.append(p)
        self.stdout.write(f'  ✓ Patients: {len(patients)} records')

        # Medicines
        meds_raw = [
            ('Paracetamol 500mg', 'Acetaminophen', 'Tablet', 'PharmaCo Uganda', 1500, 200, 20, 'Fever and pain relief'),
            ('Amoxicillin 250mg', 'Amoxycillin', 'Capsule', 'MediLabs Ltd', 3000, 150, 15, 'Broad-spectrum antibiotic'),
            ('Metformin 500mg', 'Metformin HCl', 'Tablet', 'DiabeCare', 2500, 180, 20, 'Type 2 diabetes management'),
            ('Ibuprofen 400mg', 'Ibuprofen', 'Tablet', 'PharmaCo Uganda', 2000, 120, 15, 'Anti-inflammatory, fever'),
            ('Atenolol 50mg', 'Atenolol', 'Tablet', 'CardioMed', 4000, 90, 10, 'Hypertension and angina'),
            ('Omeprazole 20mg', 'Omeprazole', 'Capsule', 'GastroCare', 3500, 100, 10, 'Stomach acid reduction'),
            ('Salbutamol Inhaler', 'Salbutamol', 'Other', 'RespiCare', 25000, 40, 5, 'Asthma and COPD reliever'),
            ('ORS Sachets', 'Oral Rehydration Salts', 'Other', 'HydraPlus', 500, 300, 30, 'Dehydration treatment'),
            ('Artemether-Lumefantrine', 'Coartem', 'Tablet', 'NovaMed', 15000, 60, 10, 'Malaria treatment'),
            ('Ciprofloxacin 500mg', 'Ciprofloxacin', 'Tablet', 'AntiBio Ltd', 4500, 80, 15, 'Antibiotic for UTI, respiratory infections'),
        ]
        medicines = []
        for name, generic, cat, mfr, price, stock, reorder, desc in meds_raw:
            m, _ = Medicine.objects.get_or_create(name=name, defaults=dict(
                generic_name=generic, category=cat, manufacturer=mfr,
                unit_price=price, stock_quantity=stock, reorder_level=reorder, description=desc))
            medicines.append(m)
        self.stdout.write(f'  ✓ Medicines: {len(medicines)} items')

        # Appointments
        appt_raw = [
            (patients[0], doctors[0], today, '09:00', 'General', 'Routine blood pressure checkup', 'Confirmed', 30000),
            (patients[1], doctors[0], today, '10:30', 'Consultation', 'Persistent headaches for 2 weeks', 'Scheduled', 50000),
            (patients[2], doctors[1], today + datetime.timedelta(1), '11:00', 'Follow-up', 'Diabetes management follow-up', 'Scheduled', 40000),
            (patients[3], doctors[1], today - datetime.timedelta(2), '14:00', 'General', 'Fever and cough for 3 days', 'Completed', 30000),
            (patients[4], doctors[0], today - datetime.timedelta(5), '08:30', 'Consultation', 'Heart palpitations and chest pain', 'Completed', 50000),
            (patients[0], doctors[1], today + datetime.timedelta(7), '15:00', 'Follow-up', 'Review lab results', 'Scheduled', 30000),
        ]
        for pat, doc, date, time_str, atype, reason, status, fee in appt_raw:
            Appointment.objects.get_or_create(
                patient=pat, doctor=doc, date=date,
                defaults=dict(time=time_str, appointment_type=atype, reason=reason,
                              status=status, fee=fee, created_by=admin))
        self.stdout.write(f'  ✓ Appointments created')

        # Consultations
        if not patients[0].consultations.exists():
            Consultation.objects.create(
                patient=patients[0], doctor=doctors[0],
                chief_complaint='High blood pressure readings at home, 160/100',
                diagnosis='Essential Hypertension Stage 2',
                treatment_plan='Atenolol 50mg daily, dietary changes, exercise 30min/day',
                status='Completed', fee=50000,
                follow_up_date=today + datetime.timedelta(30))
        self.stdout.write(f'  ✓ Consultations created')

        # Vitals
        for i, p in enumerate(patients[:4]):
            if not p.vitals.exists():
                Vitals.objects.create(
                    patient=p, nurse=nurses[0],
                    temperature=str(36.5 + i * 0.2),
                    blood_pressure=f'{110 + i * 8}/{70 + i * 4}',
                    pulse=str(72 + i * 4),
                    weight=str(62 + i * 6),
                    height=str(165 + i * 3),
                    oxygen_saturation=str(98 - i),
                    notes='Vitals recorded during routine check')
        self.stdout.write(f'  ✓ Vitals recorded')

        # Medical Records
        records_raw = [
            (patients[0], doctors[0], 'Essential Hypertension', 'Headache, dizziness, elevated BP 160/100', 'Atenolol 50mg daily, low-sodium diet'),
            (patients[1], doctors[0], 'Tension-type Headache', 'Bilateral throbbing headache, neck stiffness', 'Ibuprofen 400mg TDS, rest, hydration, reduce screen time'),
            (patients[2], doctors[1], 'Type 2 Diabetes Mellitus', 'Polyuria, polydipsia, fatigue, weight loss', 'Metformin 500mg BD, diabetic diet, glucose monitoring'),
            (patients[3], doctors[1], 'Acute Upper Respiratory Infection', 'Fever 38.5°C, productive cough, sore throat', 'Amoxicillin 500mg TDS 7 days, paracetamol PRN, fluids'),
        ]
        for pat, doc, diag, symp, treat in records_raw:
            if not pat.medical_records.exists():
                MedicalRecord.objects.create(
                    patient=pat, doctor=doc, diagnosis=diag,
                    symptoms=symp, treatment=treat,
                    notes='Patient reviewed and counselled')
        self.stdout.write(f'  ✓ Medical records added')

        # Lab Results
        if not patients[0].lab_results.exists():
            LabResult.objects.create(patient=patients[0], doctor=doctors[0],
                test_name='Complete Blood Count (CBC)',
                result='WBC: 7.2×10⁹/L, RBC: 4.8×10¹²/L, Hgb: 14.2g/dL, Hct: 42%, Plt: 280×10⁹/L',
                reference_range='WBC: 4.0-11.0, RBC: 4.5-5.5, Hgb: 13-17, Plt: 150-400',
                status='Normal', notes='All haematological parameters within normal limits')
            LabResult.objects.create(patient=patients[0], doctor=doctors[0],
                test_name='Fasting Blood Glucose',
                result='126 mg/dL (7.0 mmol/L)',
                reference_range='Normal: 70-99 mg/dL; Prediabetes: 100-125; Diabetes: ≥126',
                status='Abnormal', notes='Borderline diabetic - recommend HbA1c and repeat FBG. Dietary counselling given.')
            LabResult.objects.create(patient=patients[0], doctor=doctors[0],
                test_name='Renal Function Test',
                result='Creatinine: 88 µmol/L, Urea: 5.2 mmol/L, eGFR: 85 mL/min',
                reference_range='Creatinine: 62-115, Urea: 2.5-7.8, eGFR: >60',
                status='Normal', notes='Renal function within acceptable range')
        self.stdout.write(f'  ✓ Lab results added')

        # Prescriptions
        if not patients[0].prescriptions.exists():
            rx = Prescription.objects.create(patient=patients[0], doctor=doctors[0], status='Active',
                notes='Take all medications as directed. Do not stop without consulting doctor.')
            PrescriptionItem.objects.create(prescription=rx, medicine=medicines[4],
                dosage='50mg', frequency='Once daily (morning)', duration='30 days', quantity=30,
                instructions='Take with or without food. Monitor BP weekly.')
            PrescriptionItem.objects.create(prescription=rx, medicine=medicines[0],
                dosage='500mg', frequency='Three times daily', duration='7 days', quantity=21,
                instructions='Take after meals. Avoid on empty stomach.')

        if not patients[2].prescriptions.exists():
            rx2 = Prescription.objects.create(patient=patients[2], doctor=doctors[1], status='Active',
                notes='Strict diabetic diet required alongside medication.')
            PrescriptionItem.objects.create(prescription=rx2, medicine=medicines[2],
                dosage='500mg', frequency='Twice daily', duration='90 days', quantity=180,
                instructions='Take with first bite of main meals.')
        self.stdout.write(f'  ✓ Prescriptions issued')

        # Bills
        for pat in patients[:4]:
            if not pat.bills.exists():
                bill = Bill.objects.create(patient=pat, created_by=admin, status='Pending',
                    due_date=today + datetime.timedelta(30))
                BillItem.objects.create(bill=bill, item_type='Consultation', description='Doctor Consultation Fee',
                    quantity=1, unit_price=50000, amount=50000)
                BillItem.objects.create(bill=bill, item_type='Lab', description='Laboratory Tests Panel',
                    quantity=1, unit_price=35000, amount=35000)
                if pat.prescriptions.exists():
                    BillItem.objects.create(bill=bill, item_type='Medicine', description='Prescribed Medications',
                        quantity=1, unit_price=28500, amount=28500)

        # Paid patient (discharged)
        if not patients[4].bills.exists():
            bill5 = Bill.objects.create(patient=patients[4], created_by=admin, status='Paid')
            BillItem.objects.create(bill=bill5, item_type='Consultation', description='Cardiology Consultation',
                quantity=1, unit_price=75000, amount=75000)
            BillItem.objects.create(bill=bill5, item_type='Lab', description='ECG & Cardiac Enzymes',
                quantity=1, unit_price=120000, amount=120000)
            Payment.objects.get_or_create(
                patient=patients[4], bill=bill5,
                defaults=dict(payment_method='MTN_MOMO', amount=195000,
                    phone_number='+256770111222', transaction_id='MTN-DEMO-98765',
                    status='Success', initiated_by=admin))
        self.stdout.write(f'  ✓ Bills and payments created')

        # Notifications
        for pu in patient_users:
            Notification.objects.get_or_create(
                recipient=pu, title='Welcome to MediCare HMS',
                defaults=dict(message='Your patient portal is ready. Book appointments, view results and pay bills online.',
                    notification_type='general'))
        for doc in doctors:
            Notification.objects.get_or_create(
                recipient=doc, title='Patients Assigned',
                defaults=dict(message='You have patients assigned to you. Review your dashboard.',
                    notification_type='general'))
        self.stdout.write(f'  ✓ Notifications sent')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Demo data seeded successfully!'))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Demo Login Credentials:'))
        self.stdout.write('  Admin:   admin       / admin123')
        self.stdout.write('  Doctor:  dr.sarah    / pass@123')
        self.stdout.write('  Nurse:   nurse.alice / pass@123')
        self.stdout.write('  Patient: john.patient/ pass@123')
