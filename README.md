# 🏥 MediCare Hospital Management System

A complete, production-ready Hospital Management System built with **Django** (backend) and **Bootstrap 5 + JavaScript** (frontend). Converted from a Tkinter desktop app to a fully responsive full-stack web application.

---

## ✨ Features

### 👥 Role-Based Access Control
| Role | Access |
|------|--------|
| **Admin** | Full system control — users, patients, reports, billing, all modules |
| **Doctor** | Assigned patients, consultations, prescriptions, lab results, medical records |
| **Nurse** | Patient vitals, patient info, appointment assistance |
| **Patient** | Own dashboard, appointments, bills, lab results, prescriptions, medicine orders |

### 🏥 Core Modules
- **Patient Management** — Full profiles, medical history, vitals, lab results, status tracking
- **Appointments** — Booking, approval, reschedule, cancellation with status workflow
- **Consultations** — Request flow with billing at configurable fee (default UGX 50,000)
- **Pharmacy** — Medicine inventory, prescriptions with multi-item support, medicine orders
- **Billing** — Auto-generated invoices per service, printable PDF invoices/receipts
- **Payments** — MTN Mobile Money & Airtel Money integration with webhook support
- **Notifications** — Real-time in-app alerts for appointments, payments, lab results, prescriptions
- **Reports & Analytics** — Chart.js dashboards with monthly trends, revenue, appointment stats

### 💳 Payment Integration
- **MTN Mobile Money** — Full API integration (sandbox + production ready)
- **Airtel Money** — OAuth2 + payment API integration
- **Cash payments** — Instant recording
- Webhook endpoints for payment status callbacks
- Polling-based status check on frontend

---

## 🚀 Quick Start

### 1. Clone / Unzip the project
```bash
cd medicare_hms
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your API credentials
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser (optional — demo admin already seeded)
```bash
python manage.py createsuperuser
```

### 7. Start the server
```bash
python manage.py runserver
```

### 8. Open in browser
```
http://127.0.0.1:8000/
```

---

## 🔑 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Doctor | `doctor1` | `doctor123` |
| Nurse | `nurse1` | `nurse123` |
| Patient | `patient1` | `patient123` |

---

## 📁 Project Structure

```
medicare_hms/
├── medicare_hms/          # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                 # Auth, roles, dashboard
├── patients/              # Patient records, vitals, labs
├── appointments/          # Appointments & consultations
├── pharmacy/              # Medicines, prescriptions, orders
├── billing/               # Bills, invoices, receipts
├── payments/              # MTN MoMo, Airtel Money, webhooks
├── reports/               # Analytics dashboard (Chart.js)
├── notifications/         # In-app notification system
├── templates/             # All HTML templates
│   ├── base.html          # Main layout with sidebar
│   ├── users/
│   ├── patients/
│   ├── appointments/
│   ├── pharmacy/
│   ├── billing/
│   ├── payments/
│   ├── reports/
│   └── notifications/
├── static/                # CSS, JS, images
├── media/                 # Uploaded files
├── hospital.db            # SQLite database (auto-created)
├── requirements.txt
├── .env.example
└── manage.py
```

---

## 💰 Payment Gateway Setup

### MTN Mobile Money
1. Register at [MTN MoMo Developer Portal](https://momodeveloper.mtn.com)
2. Create an API User and API Key for "Collection"
3. Set in `.env`: 
```
MTN_MOMO_SUBSCRIPTION_KEY=...
MTN_MOMO_API_USER=...
MTN_MOMO_API_KEY=...
MTN_MOMO_ENVIRONMENT=sandbox  # or production
```
4. Webhook URL: `https://yourdomain.com/payments/webhook/mtn/`

### Airtel Money
1. Register at [Airtel Developer Portal](https://developers.airtel.africa)
2. Get Client ID and Client Secret
3. Set in `.env`:
```
AIRTEL_CLIENT_ID=...
AIRTEL_CLIENT_SECRET=...
AIRTEL_BASE_URL=https://openapiuat.airtel.africa  # or live URL
```
4. Webhook URL: `https://yourdomain.com/payments/webhook/airtel/`

> **Note:** Without API credentials, payments fall back to **simulation mode** (auto-approve) — perfect for development/testing.

---

## 🛠️ Production Deployment

### Using Gunicorn + Nginx

```bash
# Install gunicorn (already in requirements.txt)
gunicorn medicare_hms.wsgi:application --bind 0.0.0.0:8000

# Collect static files
python manage.py collectstatic
```

### Environment settings for production
```
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=<long-random-string>
```

---

## 🔒 Security Notes

- API credentials stored in `.env` (never commit to version control)
- CSRF protection enabled on all forms
- Role-based view protection via decorators
- Password hashing via Django's built-in system (PBKDF2 + SHA256)
- Media files served separately (configure CDN in production)

---

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2, Python 3.10+ |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Bootstrap 5.3, Bootstrap Icons |
| Charts | Chart.js 4.4 |
| Payments | MTN MoMo API, Airtel Money API |
| Auth | Django Auth + Custom User Model |
| Media | Django FileField + Pillow |

---

## 📞 Support & Customization

- To switch to **PostgreSQL**: update `DATABASES` in `settings.py`
- To add **email notifications**: configure `EMAIL_BACKEND` and SMTP settings
- To add **PDF generation**: the invoice template at `billing/invoice.html` is print-ready
- To customize **consultation fee**: set `CONSULTATION_FEE` in `.env`

---

*MediCare HMS — Built with ❤️ for healthcare management in Uganda*
# medicare
