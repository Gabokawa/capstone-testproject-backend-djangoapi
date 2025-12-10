from rest_framework import serializers
from .models import (
    Professional,
    ProfessionalDocument,
    WorkingHours,
    ProfessionalService
)
from users.serializers import UserSerializer
from services.serializers import ServiceSerializer

# ==================== PROFESSIONAL SERIALIZER ====================
# class ProfessionalSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)

#     class Meta:
#         model = Professional
#         fields = [
#             'professional_id',
#             'user',
#             'business_name',
#             'bio',
#             'rating',
#             'total_reviews',
#             'completed_jobs',
#             'is_verified',
#             'is_available',
#             'availability_notes',
#             'last_active',
#             'service_radius_km',
#         ]

class ProfessionalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specialties = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()
    estimated_arrival = serializers.SerializerMethodField()
    hourly_rate = serializers.SerializerMethodField()
    service_fee = serializers.SerializerMethodField()
    
    class Meta:
        model = Professional
        fields = [
            'professional_id',
            'user',
            'business_name',
            'bio',
            'rating',
            'total_reviews',
            'completed_jobs',
            'is_verified',
            'is_available',
            'availability_notes',
            'last_active',
            'service_radius_km',
            'specialties',
            'distance_km',
            'estimated_arrival',
            'hourly_rate',
            'service_fee',
        ]
    
    def get_specialties(self, obj):
        # If we have a related model for specialties, fetch them
        # Otherwise return empty list or mock data
        return []
    
    def get_distance_km(self, obj):
        # Calculated based on user's location and professional's location
        # for now, return None or mock value
        return None
    
    def get_estimated_arrival(self, obj):
        # Calculate based on distance
        # for now, return mock
        return None
    
    def get_hourly_rate(self, obj):
        # If we get this in the model or somewhere else, return it
        return None
    
    def get_service_fee(self, obj):
        # If we get this in the model or somewhere else, return it
        return None


# ==================== PROFESSIONAL DOCUMENT SERIALIZER ====================
class ProfessionalDocumentSerializer(serializers.ModelSerializer):
    professional = ProfessionalSerializer(read_only=True)

    class Meta:
        model = ProfessionalDocument
        fields = [
            'document_id',
            'professional',
            'document_type',
            'document_name',
            'document_uri',
            'is_verified',
            'uploaded_at',
            'verified_at',
            'verified_by_admin_id',
        ]


# ==================== WORKING HOURS SERIALIZER ====================
class WorkingHoursSerializer(serializers.ModelSerializer):
    professional = ProfessionalSerializer(read_only=True)

    class Meta:
        model = WorkingHours
        fields = [
            'hours_id',
            'professional',
            'day_of_week',
            'start_time',
            'end_time',
            'is_available',
        ]


# ==================== PROFESSIONAL SERVICE SERIALIZER ====================
class ProfessionalServiceSerializer(serializers.ModelSerializer):
    professional = ProfessionalSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = ProfessionalService
        fields = [
            'prof_service_id',
            'professional',
            'service',
            'custom_price_range',
            'service_notes',
            'estimated_duration_minutes',
            'is_available',
        ]