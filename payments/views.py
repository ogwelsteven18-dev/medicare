from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Payment
from billing.models import Bill
from patients.models import Patient
from notifications.models import send_notification
import uuid, json, requests, base64, datetime

@login_required
def payment_list(request):
    user = request.user
    payments = Payment.objects.select_related('patient','bill').all()
    if user.role == 'patient':
        try: payments = payments.filter(patient=user.patient_profile)
        except: payments = payments.none()
    return render(request, 'payments/payment_list.html', {'payments': payments})

@login_required
def initiate_payment(request, bill_id):
    bill = get_object_or_404(Bill, pk=bill_id)
    if request.user.role == 'patient':
        try:
            if bill.patient != request.user.patient_profile:
                messages.error(request, 'Access denied.'); return redirect('billing:bill_list')
        except: messages.error(request, 'Access denied.'); return redirect('billing:bill_list')
    if request.method == 'POST':
        method = request.POST.get('payment_method')
        phone = request.POST.get('phone_number','').strip()
        amount = bill.balance
        if amount <= 0:
            messages.info(request, 'Bill is already fully paid.'); return redirect('billing:bill_detail', pk=bill_id)
        payment = Payment.objects.create(
            patient=bill.patient, bill=bill, payment_method=method,
            amount=amount, phone_number=phone,
            external_ref=str(uuid.uuid4()), initiated_by=request.user,
            status='Pending'
        )
        if method == 'MTN_MOMO':
            result = initiate_mtn_payment(payment, phone, float(amount))
        elif method == 'AIRTEL':
            result = initiate_airtel_payment(payment, phone, float(amount))
        elif method == 'CASH':
            payment.status = 'Success'
            payment.transaction_id = f'CASH-{payment.pk}-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
            payment.save()
            _finalize_payment(payment)
            messages.success(request, 'Cash payment recorded successfully.')
            return redirect('payments:receipt', pk=payment.pk)
        else:
            payment.status = 'Failed'
            payment.save()
            messages.error(request, 'Unsupported payment method.')
            return redirect('billing:bill_detail', pk=bill_id)
        if result.get('success'):
            messages.info(request, 'Payment initiated. Please complete on your phone.')
            return redirect('payments:payment_status', pk=payment.pk)
        else:
            messages.error(request, result.get('error', 'Payment initiation failed.'))
            return redirect('billing:bill_detail', pk=bill_id)
    return render(request, 'payments/initiate_payment.html', {'bill': bill})

def initiate_mtn_payment(payment, phone, amount):
    try:
        sub_key = settings.MTN_MOMO_SUBSCRIPTION_KEY
        base_url = settings.MTN_MOMO_BASE_URL
        environment = settings.MTN_MOMO_ENVIRONMENT
        headers = {
            'Ocp-Apim-Subscription-Key': sub_key,
            'X-Target-Environment': environment,
            'Content-Type': 'application/json',
        }
        # Request to pay
        payload = {
            "amount": str(int(amount)),
            "currency": "UGX",
            "externalId": payment.external_ref,
            "payer": {"partyIdType": "MSISDN", "partyId": phone},
            "payerMessage": f"Hospital Bill Payment #{payment.bill.invoice_number}",
            "payeeNote": "MediCare HMS Payment"
        }
        api_user = settings.MTN_MOMO_API_USER
        api_key = settings.MTN_MOMO_API_KEY
        if not api_user or not api_key:
            # Sandbox simulation
            payment.transaction_id = f"MTN-SIM-{payment.external_ref[:8]}"
            payment.status = 'Processing'
            payment.save()
            return {'success': True}
        token_resp = requests.post(
            f"{base_url}/collection/token/",
            auth=(api_user, api_key),
            headers={'Ocp-Apim-Subscription-Key': sub_key}
        )
        token = token_resp.json().get('access_token')
        headers['Authorization'] = f'Bearer {token}'
        headers['X-Reference-Id'] = payment.external_ref
        resp = requests.post(f"{base_url}/collection/v1_0/requesttopay", json=payload, headers=headers)
        if resp.status_code == 202:
            payment.status = 'Processing'
            payment.transaction_id = payment.external_ref
            payment.save()
            return {'success': True}
        return {'success': False, 'error': f'MTN API error: {resp.status_code}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def initiate_airtel_payment(payment, phone, amount):
    try:
        base_url = settings.AIRTEL_BASE_URL
        client_id = settings.AIRTEL_CLIENT_ID
        client_secret = settings.AIRTEL_CLIENT_SECRET
        if not client_id or not client_secret:
            payment.transaction_id = f"AIRTEL-SIM-{payment.external_ref[:8]}"
            payment.status = 'Processing'
            payment.save()
            return {'success': True}
        auth_resp = requests.post(f"{base_url}/auth/oauth2/token",
            json={"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"})
        token = auth_resp.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'X-Country': 'UG', 'X-Currency': 'UGX'}
        payload = {
            "reference": payment.external_ref,
            "subscriber": {"country": "UG", "currency": "UGX", "msisdn": phone},
            "transaction": {"amount": int(amount), "country": "UG", "currency": "UGX", "id": payment.external_ref}
        }
        resp = requests.post(f"{base_url}/merchant/v2/payments/", json=payload, headers=headers)
        if resp.status_code in [200, 202]:
            payment.status = 'Processing'
            payment.transaction_id = resp.json().get('data', {}).get('transaction', {}).get('id', payment.external_ref)
            payment.save()
            return {'success': True}
        return {'success': False, 'error': f'Airtel API error: {resp.status_code}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _finalize_payment(payment):
    bill = payment.bill
    if bill:
        paid = sum(p.amount for p in bill.payments.filter(status='Success'))
        if paid >= bill.total:
            bill.status = 'Paid'
        elif paid > 0:
            bill.status = 'Partial'
        bill.save()
    if payment.patient.user:
        send_notification(payment.patient.user, 'Payment Confirmed', f'Your payment of UGX {payment.amount:,.0f} was successful. Ref: {payment.transaction_id}', 'payment', f'/payments/receipt/{payment.pk}/')

@login_required
def payment_status(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.GET.get('check'):
        # Simulate check: if Processing set to Success for demo
        if payment.status == 'Processing':
            payment.status = 'Success'
            payment.save()
            _finalize_payment(payment)
        return JsonResponse({'status': payment.status})
    return render(request, 'payments/payment_status.html', {'payment': payment})

@login_required
def receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, 'payments/receipt.html', {'payment': payment, 'today': datetime.date.today()})

@csrf_exempt
def mtn_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ref = data.get('externalId') or data.get('financialTransactionId')
        status = data.get('status','')
        try:
            payment = Payment.objects.get(external_ref=ref)
            payment.webhook_data = data
            if status == 'SUCCESSFUL':
                payment.status = 'Success'
                payment.transaction_id = data.get('financialTransactionId', payment.transaction_id)
                _finalize_payment(payment)
            elif status in ['FAILED','REJECTED']:
                payment.status = 'Failed'
                payment.status_reason = data.get('reason','')
            payment.save()
        except Payment.DoesNotExist: pass
    return JsonResponse({'status': 'ok'})

@csrf_exempt
def airtel_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ref = data.get('transaction', {}).get('id','')
        status = data.get('transaction', {}).get('status','')
        try:
            payment = Payment.objects.filter(transaction_id=ref).first() or Payment.objects.filter(external_ref=ref).first()
            if payment:
                payment.webhook_data = data
                if status == 'TS':
                    payment.status = 'Success'
                    _finalize_payment(payment)
                elif status in ['TF','TA']:
                    payment.status = 'Failed'
                payment.save()
        except: pass
    return JsonResponse({'status': 'ok'})
