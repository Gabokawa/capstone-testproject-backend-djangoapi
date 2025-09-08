from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from quotes.models import Booking

class Review(models.Model):
    """Customer reviews for completed services"""
    review_id = models.AutoField(primary_key=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True)
    has_response = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'reviews'
        db_table = 'reviews'
    
    def __str__(self):
        return f"{self.booking} - {self.rating}/5"


class ReviewResponse(models.Model):
    """Professional responses to customer reviews"""
    response_id = models.AutoField(primary_key=True)
    review = models.OneToOneField(Review, on_delete=models.CASCADE)
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'reviews'
        db_table = 'review_responses'
    
    def __str__(self):
        return f"Response to {self.review}"