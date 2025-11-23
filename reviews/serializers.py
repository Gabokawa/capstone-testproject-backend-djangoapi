# reviews/serializers.py
from rest_framework import serializers
from .models import Review, ReviewResponse
from quotes.models import Booking

class ReviewSerializer(serializers.ModelSerializer):
    # Read-only fields for additional context
    customer_name = serializers.SerializerMethodField()
    professional_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(),
        source='booking',
        write_only=True
    )
    
    class Meta:
        model = Review
        fields = [
            'review_id',
            'booking',
            'booking_id',
            'rating',
            'review_text',
            'created_at',
            'is_visible',
            'has_response',
            'customer_name',
            'professional_name',
            'service_name'
        ]
        read_only_fields = ['review_id', 'created_at', 'has_response', 'booking']
    
    def get_customer_name(self, obj):
        try:
            return f"{obj.booking.request.customer.user.first_name} {obj.booking.request.customer.user.last_name}"
        except:
            return "Unknown"
    
    def get_professional_name(self, obj):
        try:
            return f"{obj.booking.quote.professional.user.first_name} {obj.booking.quote.professional.user.last_name}"
        except:
            return "Unknown"
    
    def get_service_name(self, obj):
        try:
            return obj.booking.request.service_type.name
        except:
            return "Unknown"
    
    def validate_booking(self, value):
        """Ensure booking is completed before allowing review"""
        if value.status != 'completed':
            raise serializers.ValidationError("Can only review completed bookings")
        
        # Check if review already exists
        if Review.objects.filter(booking=value).exists():
            raise serializers.ValidationError("Review already exists for this booking")
        
        return value


class ReviewResponseSerializer(serializers.ModelSerializer):
    review_id = serializers.PrimaryKeyRelatedField(
        queryset=Review.objects.all(),
        source='review',
        write_only=True
    )
    review_details = ReviewSerializer(source='review', read_only=True)
    
    class Meta:
        model = ReviewResponse
        fields = [
            'response_id',
            'review',
            'review_id',
            'response_text',
            'created_at',
            'review_details'
        ]
        read_only_fields = ['response_id', 'created_at', 'review']
    
    def validate_review(self, value):
        """Ensure only one response per review"""
        if ReviewResponse.objects.filter(review=value).exists():
            raise serializers.ValidationError("Response already exists for this review")
        return value
    
    def create(self, validated_data):
        """Update review's has_response flag when creating response"""
        response = super().create(validated_data)
        response.review.has_response = True
        response.review.save()
        return response


class ReviewListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing reviews"""
    customer_name = serializers.SerializerMethodField()
    professional_name = serializers.SerializerMethodField()
    has_response_text = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'review_id',
            'rating',
            'review_text',
            'created_at',
            'is_visible',
            'has_response',
            'customer_name',
            'professional_name',
            'has_response_text'
        ]
    
    def get_customer_name(self, obj):
        try:
            return f"{obj.booking.request.customer.user.first_name} {obj.booking.request.customer.user.last_name}"
        except:
            return "Unknown"
    
    def get_professional_name(self, obj):
        try:
            return f"{obj.booking.quote.professional.user.first_name} {obj.booking.quote.professional.user.last_name}"
        except:
            return "Unknown"
    
    def get_has_response_text(self, obj):
        """Get the response text if it exists"""
        try:
            return obj.reviewresponse.response_text
        except ReviewResponse.DoesNotExist:
            return None