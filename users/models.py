from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

# class User(AbstractUser):
#     username = models.CharField(max_length=150, unique=True)
#     password = models.CharField(max_length=128)

#     def __str__(self):
#         return self.username

class UserRole(models.Model):
    """User role definitions for RBAC"""
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100)
    description = models.TextField()
    
    class Meta:
        db_table = 'user_roles'
    
    def __str__(self):
        return self.role_name


class User(AbstractUser):
    """Extended user model with device repair service specific fields"""
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('repairman', 'Repairman'),
        ('admin', 'Admin'),
    ]
    
    user_id = models.AutoField(primary_key=True, default=None)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    profile_picture = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    device_token = models.CharField(max_length=500, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class UserRoleMapping(models.Model):
    """Many-to-many relationship between users and roles"""
    mapping_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_role_mapping'
    
    def __str__(self):
        return f"{self.user} - {self.role}"


class Address(models.Model):
    """User address management"""
    address_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    region = models.CharField(max_length=100)
    full_address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'addresses'
    
    def __str__(self):
        return f"{self.user} - {self.region}"
