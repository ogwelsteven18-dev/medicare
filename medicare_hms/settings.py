import os
from pathlib import Path

try:
    from decouple import config
except ImportError:
    def config(key, default=None, cast=None):
        val = os.environ.get(key, default)
        if cast and val is not None:
            return cast(val)
        return val

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-medicare-hms-key-change-in-prod-2024')
DEBUG = True
ALLOWED_HOSTS = ['medicare-5pf5.onrender.com', '127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'patients',
    'appointments',
    'pharmacy',
    'billing',
    'payments',
    'reports',
    'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'medicare_hms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notifications.context_processors.unread_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'medicare_hms.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'hospital.db',
    }
}

AUTH_USER_MODEL = 'users.User'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Kampala'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/users/dashboard/'
LOGOUT_REDIRECT_URL = '/users/login/'

MTN_MOMO_SUBSCRIPTION_KEY = os.environ.get('MTN_MOMO_SUBSCRIPTION_KEY', 'test-key')
MTN_MOMO_API_USER = os.environ.get('MTN_MOMO_API_USER', '')
MTN_MOMO_API_KEY = os.environ.get('MTN_MOMO_API_KEY', '')
MTN_MOMO_BASE_URL = os.environ.get('MTN_MOMO_BASE_URL', 'https://sandbox.momodeveloper.mtn.com')
MTN_MOMO_ENVIRONMENT = os.environ.get('MTN_MOMO_ENVIRONMENT', 'sandbox')

AIRTEL_CLIENT_ID = os.environ.get('AIRTEL_CLIENT_ID', '')
AIRTEL_CLIENT_SECRET = os.environ.get('AIRTEL_CLIENT_SECRET', '')
AIRTEL_BASE_URL = os.environ.get('AIRTEL_BASE_URL', 'https://openapiuat.airtel.africa')

CONSULTATION_FEE = 50000
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Add the deployed domain to CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = ['https://medicare-5pf5.onrender.com']
