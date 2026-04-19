from django.db import models
from users.models import User

class Notification(models.Model):
    TYPE_CHOICES = [
        ('appointment','Appointment'),('payment','Payment'),('lab','Lab Result'),
        ('prescription','Prescription'),('general','General'),('alert','Alert'),
    ]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['-created_at']
    def __str__(self): return f"Notification for {self.recipient}: {self.title}"

def send_notification(user, title, message, notification_type='general', link=''):
    Notification.objects.create(
        recipient=user, title=title, message=message,
        notification_type=notification_type, link=link
    )
