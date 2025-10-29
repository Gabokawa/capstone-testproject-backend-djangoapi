from django.db import models

# Create your models here.
from django.db import models
from users.models import User, Address
from services.models import Service

class ServiceRequest(models.Model):
    """Customer service requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('quoted', 'Quoted'),
        ('booked', 'Booked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    request_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    device_type = models.CharField(max_length=100)
    device_brand = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_for = models.DateTimeField(blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    device_model = models.CharField(max_length=100)
    device_issue_description = models.TextField()
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        app_label = 'requests'
        db_table = 'service_requests'
    
    def __str__(self):
        return f"{self.customer} - {self.service} - {self.device_type}"


class RequestMedia(models.Model):
    """Media files attached to service requests"""
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    media_id = models.AutoField(primary_key=True)
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    media_name = models.CharField(max_length=200)
    # media_uri = models.CharField(max_length=500)
    media = models.FileField(upload_to='request_media/')
    thumbnail_uri = models.CharField(max_length=500, blank=True, null=True)
    media_size = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    caption = models.CharField(max_length=500, blank=True, null=True)
    is_public = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'requests'
        db_table = 'request_media'
    
    def __str__(self):
        return f"{self.request} - {self.media_name}"
