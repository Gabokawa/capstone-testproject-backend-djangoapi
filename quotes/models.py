from django.db import models
from requests.models import ServiceRequest
from professionals.models import Professional

class Quote(models.Model):
    """Professional quotes for service requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    quote_id = models.AutoField(primary_key=True)
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)
    parts_needed = models.TextField(blank=True, null=True)
    parts_price = models.DecimalField(max_digits=10, decimal_places=2)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_quote_amount = models.DecimalField(max_digits=10, decimal_places=2)
    service_date = models.DateTimeField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    quote_description = models.TextField()
    additional_notes = models.TextField(blank=True, null=True)
    valid_until = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quotes'
        db_table = 'quotes'
    
    def __str__(self):
        return f"{self.request} - {self.professional} - ₱{self.total_quote_amount}"


class Booking(models.Model):
    """Confirmed bookings from accepted quotes"""
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    booking_id = models.AutoField(primary_key=True)
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    booking_date = models.DateTimeField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    completion_notes = models.TextField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    is_reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        app_label = 'quotes'
        db_table = 'bookings'
    
    def __str__(self):
        return f"{self.request} - {self.booking_date}"


class ServiceIssue(models.Model):
    """Service quality issues and disputes"""
    ISSUE_TYPE_CHOICES = [
        ('quality', 'Quality'),
        ('damage', 'Damage'),
        ('incomplete', 'Incomplete'),
        ('delay', 'Delay'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    issue_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by_admin_id = models.IntegerField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        app_label = 'quotes'
        db_table = 'service_issues'
    
    def __str__(self):
        return f"{self.booking} - {self.issue_type} - {self.status}"