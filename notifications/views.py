from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True; notif.save()
    return redirect(notif.link or 'notifications:notification_list')

@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect('notifications:notification_list')
