# reviews/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Review

@receiver([post_save, post_delete], sender=Review)
def update_professional_rating(sender, instance, **kwargs):
    # Get the professional from the booking
    professional = instance.booking.quote.professional
    
    # Calculate new average rating and count
    reviews = Review.objects.filter(
        booking__quote__professional=professional,
        is_visible=True
    )
    
    professional.rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    professional.total_reviews = reviews.count()
    professional.save(update_fields=['rating', 'total_reviews'])
