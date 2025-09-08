from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from services.models import Service

class Professional(models.Model):
    """Professional service provider profiles"""
    professional_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    bio = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    total_reviews = models.IntegerField(default=0)
    completed_jobs = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    availability_notes = models.TextField(blank=True, null=True)
    last_active = models.DateTimeField(auto_now=True)
    service_radius_km = models.DecimalField(max_digits=5, decimal_places=2)
    
    class Meta:
        app_label = 'professionals'
        db_table = 'professionals'
    
    def __str__(self):
        return f"{self.user} - {self.business_name}"


class ProfessionalDocument(models.Model):
    """Professional verification documents"""
    DOCUMENT_TYPE_CHOICES = [
        ('license', 'License'),
        ('certification', 'Certification'),
        ('insurance', 'Insurance'),
        ('id_card', 'ID Card'),
    ]
    
    document_id = models.AutoField(primary_key=True)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    document_name = models.CharField(max_length=200)
    document_uri = models.CharField(max_length=500)
    is_verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by_admin_id = models.IntegerField(blank=True, null=True)
    
    class Meta:
        app_label = 'professionals'
        db_table = 'professional_documents'
    
    def __str__(self):
        return f"{self.professional} - {self.document_type}"


class WorkingHours(models.Model):
    """Professional working hours schedule"""
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    hours_id = models.AutoField(primary_key=True)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'professionals'
        db_table = 'working_hours'
    
    def __str__(self):
        return f"{self.professional} - {self.day_of_week}"


class ProfessionalService(models.Model):
    """Services offered by professionals with custom pricing"""
    prof_service_id = models.AutoField(primary_key=True)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    custom_price_range = models.CharField(max_length=100, blank=True, null=True)
    service_notes = models.TextField(blank=True, null=True)
    estimated_duration_minutes = models.IntegerField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'professionals'
        db_table = 'professional_services'
    
    def __str__(self):
        return f"{self.professional} - {self.service}"