from django.db import models
from users.models import User

class Notification(models.Model):
    """System notifications for users"""
    NOTIFICATION_TYPE_CHOICES = [
        ('request', 'Request'),
        ('quote', 'Quote'),
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('system', 'System'),
    ]
    
    RELATED_ENTITY_CHOICES = [
        ('service_request', 'Service Request'),
        ('booking', 'Booking'),
        ('payment', 'Payment'),
    ]
    
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
    related_entity = models.CharField(max_length=20, choices=RELATED_ENTITY_CHOICES, blank=True, null=True)
    related_entity_id = models.IntegerField(blank=True, null=True)
    
    class Meta:
        app_label = 'notifications'
        db_table = 'notifications'
    
    def __str__(self):
        return f"{self.user} - {self.title}"
