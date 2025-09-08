from django.db import models
from quotes.models import Booking

class Payment(models.Model):
    """Payment transactions for bookings"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('digital_wallet', 'Digital Wallet'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    payment_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_reference = models.CharField(max_length=200)
    payment_date = models.DateTimeField()
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    refund_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'payments'
        db_table = 'payments'
    
    def __str__(self):
        return f"{self.booking} - ₱{self.amount} - {self.status}"


class PaymentTransaction(models.Model):
    """Third-party payment provider transaction details"""
    PROVIDER_CHOICES = [
        ('gcash', 'GCash'),
        ('paymaya', 'PayMaya'),
    ]
    
    transaction_id = models.AutoField(primary_key=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_transaction_id = models.CharField(max_length=200)
    provider_reference = models.CharField(max_length=200)
    provider_status = models.CharField(max_length=100)
    provider_response = models.TextField()
    provider_fee = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'payments'
        db_table = 'payment_transactions'
    
    def __str__(self):
        return f"{self.payment} - {self.provider} - {self.provider_transaction_id}"