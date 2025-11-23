# reviews/views.py
from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Avg
from .models import Review, ReviewResponse
from .serializers import (
    ReviewSerializer, 
    ReviewResponseSerializer,
    ReviewListSerializer
)
from quotes.models import Booking

class ReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Reviews
    
    List: GET /reviews/
    Create: POST /reviews/
    Retrieve: GET /reviews/{id}/
    Update: PUT/PATCH /reviews/{id}/
    Delete: DELETE /reviews/{id}/
    
    Custom actions:
    - my_reviews: GET /reviews/my_reviews/
    - professional_reviews: GET /reviews/professional_reviews/{professional_id}/
    - booking_review: GET /reviews/booking_review/{booking_id}/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    search_fields = ['review_text']
    
    def get_queryset(self):
        """Filter reviews based on user role and visibility"""
        user = self.request.user
        queryset = Review.objects.select_related(
            'booking__request__customer',
            'booking__quote__professional__user'
        ).all()
        
        # Filter by visibility for non-owners
        if not (hasattr(user, 'customer') or hasattr(user, 'professional')):
            queryset = queryset.filter(is_visible=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return ReviewListSerializer
        return ReviewSerializer
    
    def perform_create(self, serializer):
        """Validate user owns the booking before creating review"""
        booking = serializer.validated_data['booking']
        user = self.request.user
        
        # Check if user is the customer who made the booking
        if user.user_type != 'customer':
            raise serializers.ValidationError("Only customers can create reviews")
        
        if booking.request.customer != user:
            raise serializers.ValidationError("You can only review your own bookings")
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Only allow customer who created review to update it"""
        review = self.get_object()
        
        if not hasattr(self.request.user, 'customer'):
            raise serializers.ValidationError("Only customers can update reviews")
        
        if review.booking.request.customer != self.request.user.customer:
            raise serializers.ValidationError("You can only update your own reviews")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only allow customer who created review to delete it"""
        if not hasattr(self.request.user, 'customer'):
            raise serializers.ValidationError("Only customers can delete reviews")
        
        if instance.booking.request.customer != self.request.user.customer:
            raise serializers.ValidationError("You can only delete your own reviews")
        
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get all reviews created by the logged-in customer"""
        if not hasattr(request.user, 'customer'):
            return Response(
                {"error": "Only customers can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reviews = self.get_queryset().filter(
            booking__request__customer=request.user.customer
        )
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='professional/(?P<professional_id>[^/.]+)')
    def professional_reviews(self, request, professional_id=None):
        """Get all reviews for a specific professional with average rating"""
        reviews = self.get_queryset().filter(
            booking__quote__professional_id=professional_id,
            is_visible=True
        )
        
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        
        serializer = self.get_serializer(reviews, many=True)
        return Response({
            'reviews': serializer.data,
            'average_rating': round(avg_rating, 2) if avg_rating else 0,
            'total_reviews': reviews.count()
        })
    
    @action(detail=False, methods=['get'], url_path='booking/(?P<booking_id>[^/.]+)')
    def booking_review(self, request, booking_id=None):
        """Get review for a specific booking"""
        try:
            review = self.get_queryset().get(booking_id=booking_id)
            serializer = self.get_serializer(review)
            return Response(serializer.data)
        except Review.DoesNotExist:
            return Response(
                {"error": "Review not found for this booking"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['patch'])
    def toggle_visibility(self, request, pk=None):
        """Toggle review visibility (admin/professional only)"""
        review = self.get_object()
        
        # Only professional can toggle visibility of their reviews
        if hasattr(request.user, 'professional'):
            if review.booking.quote.professional != request.user.professional:
                return Response(
                    {"error": "You can only toggle visibility of your own reviews"},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {"error": "Only professionals can toggle review visibility"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        review.is_visible = not review.is_visible
        review.save()
        
        serializer = self.get_serializer(review)
        return Response(serializer.data)


class ReviewResponseViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Review Responses
    
    List: GET /api/review-responses/
    Create: POST /api/review-responses/
    Retrieve: GET /api/review-responses/{id}/
    Update: PUT/PATCH /api/review-responses/{id}/
    Delete: DELETE /api/review-responses/{id}/
    
    Custom actions:
    - my_responses: GET /api/review-responses/my_responses/
    """
    queryset = ReviewResponse.objects.select_related('review__booking__quote__professional').all()
    serializer_class = ReviewResponseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Only allow professional to respond to their own reviews"""
        review = serializer.validated_data['review']
        
        if not hasattr(self.request.user, 'professional'):
            raise serializers.ValidationError("Only professionals can create responses")
        
        # Check if the review is for this professional's service
        if review.booking.quote.professional != self.request.user.professional:
            raise serializers.ValidationError("You can only respond to reviews of your services")
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Only allow professional who created response to update it"""
        response = self.get_object()
        
        if not hasattr(self.request.user, 'professional'):
            raise serializers.ValidationError("Only professionals can update responses")
        
        if response.review.booking.quote.professional != self.request.user.professional:
            raise serializers.ValidationError("You can only update your own responses")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only allow professional who created response to delete it"""
        if not hasattr(self.request.user, 'professional'):
            raise serializers.ValidationError("Only professionals can delete responses")
        
        if instance.review.booking.quote.professional != self.request.user.professional:
            raise serializers.ValidationError("You can only delete your own responses")
        
        # Update review's has_response flag
        instance.review.has_response = False
        instance.review.save()
        
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def my_responses(self, request):
        """Get all responses created by the logged-in professional"""
        if not hasattr(request.user, 'professional'):
            return Response(
                {"error": "Only professionals can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        responses = self.get_queryset().filter(
            review__booking__quote__professional=request.user.professional
        )
        serializer = self.get_serializer(responses, many=True)
        return Response(serializer.data)