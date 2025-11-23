# reviews/serializers.py
from rest_framework import serializers
from .models import Review, ReviewResponse
from quotes.models import Booking

class ReviewSerializer(serializers.ModelSerializer):
    # Nested customer object
    customer = serializers.SerializerMethodField()
    
    # Other fields
    booking_id = serializers.IntegerField(source='booking.booking_id', read_only=True)
    service_type = serializers.SerializerMethodField()
    device_info = serializers.SerializerMethodField()
    
    # For creating reviews
    booking_id_input = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(),
        source='booking',
        write_only=True
    )
    
    class Meta:
        model = Review
        fields = [
            'review_id',
            'booking_id',
            'booking_id_input',
            'customer',
            'rating',
            'review_text',
            'created_at',
            'is_visible',
            'has_response',
            'service_type',
            'device_info'
        ]
        read_only_fields = ['review_id', 'booking_id', 'created_at', 'has_response']
    
    def get_customer(self, obj):
        """Return customer information as nested object"""
        try:
            customer_user = obj.booking.request.customer
            return {
                'user_id': customer_user.id,
                'first_name': customer_user.first_name,
                'last_name': customer_user.last_name,
                'profile_picture': customer_user.profile_picture
            }
        except:
            return {
                'user_id': None,
                'first_name': 'Unknown',
                'last_name': '',
                'profile_picture': None
            }
    
    def get_service_type(self, obj):
        """Return the service type name"""
        try:
            return obj.booking.request.service.name
        except:
            return "Unknown"
    
    def get_device_info(self, obj):
        """Return formatted device information"""
        try:
            request = obj.booking.request
            return f"{request.device_brand} {request.device_model}"
        except:
            return "Unknown"
    
    def validate_booking_id_input(self, value):
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
    customer = serializers.SerializerMethodField()
    booking_id = serializers.IntegerField(source='booking.booking_id', read_only=True)
    service_type = serializers.SerializerMethodField()
    device_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'review_id',
            'booking_id',
            'customer',
            'rating',
            'review_text',
            'created_at',
            'is_visible',
            'has_response',
            'service_type',
            'device_info'
        ]
    
    def get_customer(self, obj):
        """Return customer information as nested object"""
        try:
            customer_user = obj.booking.request.customer
            return {
                'user_id': customer_user.id,
                'first_name': customer_user.first_name,
                'last_name': customer_user.last_name,
                'profile_picture': customer_user.profile_picture
            }
        except:
            return {
                'user_id': None,
                'first_name': 'Unknown',
                'last_name': '',
                'profile_picture': None
            }
    
    def get_service_type(self, obj):
        """Return the service type name"""
        try:
            return obj.booking.request.service.service_name
        except:
            return "Unknown"
    
    def get_device_info(self, obj):
        """Return formatted device information"""
        try:
            request = obj.booking.request
            return f"{request.device_brand} {request.device_model}"
        except:
            return "Unknown"