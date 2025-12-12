# reviews/management/commands/recalculate_ratings.py
from django.core.management.base import BaseCommand
from django.db.models import Avg
from professionals.models import Professional
from reviews.models import Review

class Command(BaseCommand):
    help = 'Recalculate all professional ratings based on their reviews'

    def handle(self, *args, **options):
        professionals = Professional.objects.all()
        updated_count = 0
        
        for professional in professionals:
            reviews = Review.objects.filter(
                booking__quote__professional=professional,
                is_visible=True
            )
            
            old_rating = professional.rating
            professional.rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            professional.total_reviews = reviews.count()
            professional.save(update_fields=['rating', 'total_reviews'])
            
            updated_count += 1
            self.stdout.write(
                f"Updated {professional.business_name}: "
                f"{old_rating} -> {professional.rating} "
                f"({professional.total_reviews} reviews)"
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} professionals'
            )
        )