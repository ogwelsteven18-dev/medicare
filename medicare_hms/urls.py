from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('users:login'), name='home'),
    path('users/', include('users.urls', namespace='users')),
    path('patients/', include('patients.urls', namespace='patients')),
    path('appointments/', include('appointments.urls', namespace='appointments')),
    path('pharmacy/', include('pharmacy.urls', namespace='pharmacy')),
    path('billing/', include('billing.urls', namespace='billing')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
