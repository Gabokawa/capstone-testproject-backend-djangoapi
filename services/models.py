from django.db import models

class ServiceCategory(models.Model):
    """Service category definitions"""
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    description = models.TextField()
    category_icon = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'services'
        db_table = 'service_categories'
        verbose_name_plural = 'Service Categories'
    
    def __str__(self):
        return self.category_name


class Service(models.Model):
    """Individual service definitions"""
    service_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)
    description = models.TextField()
    estimated_price_range = models.CharField(max_length=100)
    estimated_duration_minutes = models.IntegerField()
    service_icon = models.CharField(max_length=500)
    service_image = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'services'
        db_table = 'services'
    
    def __str__(self):
        return self.service_name
