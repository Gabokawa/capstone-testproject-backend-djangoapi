from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Quote
from .models import Booking  # adjust import path if needed

@receiver(post_save, sender=Quote)
def create_booking_when_quote_accepted(sender, instance, created, **kwargs):
    """
    Automatically create a Booking record when a quote is accepted.
    """
    # Only trigger if quote already existed and was updated (not newly created)
    if not created and instance.status == 'accepted':
        # Check if a booking already exists for this quote to prevent duplicates
        existing_booking = Booking.objects.filter(quote=instance).first()
        if existing_booking:
            return  # skip if booking already created

        # Create new booking from quote details
        Booking.objects.create(
            request=instance.request,
            quote=instance,
            booking_date=timezone.now(),
            start_time=instance.start_time,
            end_time=instance.end_time,
            final_price=instance.total_quote_amount,
        )
